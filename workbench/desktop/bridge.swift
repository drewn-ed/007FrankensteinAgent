// Trusted macOS Accessibility connector. Never evaluates generated code.
import AppKit
import ApplicationServices
import Foundation

var target: NSRunningApplication?
var refs: [String: AXUIElement] = [:]
var generation = 0
func fail(_ text: String) -> NSError { NSError(domain: "Workspace", code: 1, userInfo: [NSLocalizedDescriptionKey: text]) }
func attr(_ element: AXUIElement, _ key: String) -> AnyObject? {
    var value: CFTypeRef?
    if AXUIElementCopyAttributeValue(element, key as CFString, &value) != .success { return nil }
    return value
}
func text(_ element: AXUIElement, _ key: String) -> String { (attr(element, key) as? String ?? "").prefix(500).description }
func status() -> [String: Any] {
    return ["available": true, "trusted": AXIsProcessTrusted(), "connected": target != nil,
            "applications": NSWorkspace.shared.runningApplications.filter { $0.activationPolicy == .regular && $0.bundleIdentifier != nil }.map { ["bundle_id": $0.bundleIdentifier!, "name": $0.localizedName ?? $0.bundleIdentifier!] }]
}
func snapshot() throws -> [String: Any] {
    guard AXIsProcessTrusted() else { throw fail("macOS Accessibility permission is required for the process running Workspace. Enable it in System Settings > Privacy & Security > Accessibility, then reconnect.") }
    guard let app = target, !app.isTerminated else { throw fail("Connect a running desktop application first.") }
    let root = AXUIElementCreateApplication(app.processIdentifier)
    AXUIElementSetMessagingTimeout(root, 1.0)
    refs.removeAll(); generation += 1
    var elements: [[String: Any]] = []
    var strings: [String] = []
    var visited = 0
    let deadline = Date().addingTimeInterval(10)
    func walk(_ element: AXUIElement, _ depth: Int) {
        if Date() > deadline || depth > 14 || visited > 500 || elements.count >= 120 { return }; visited += 1
        let role = text(element, kAXRoleAttribute)
        // Do not inspect protected text values.
        if text(element, kAXSubroleAttribute) == kAXSecureTextFieldSubrole { return }
        let title = text(element, kAXTitleAttribute)
        let desc = text(element, kAXDescriptionAttribute)
        let value = text(element, kAXValueAttribute)
        let name = !title.isEmpty ? title : (!desc.isEmpty ? desc : value)
        if !name.isEmpty { strings.append(name) }
        var names: CFArray?
        AXUIElementCopyActionNames(element, &names)
        let actions = (names as? [String] ?? []).filter { $0 == kAXPressAction || $0 == kAXConfirmAction }
        var settable = DarwinBoolean(false)
        AXUIElementIsAttributeSettable(element, kAXValueAttribute as CFString, &settable)
        if !actions.isEmpty || settable.boolValue {
            let ref = "d\(generation)_\(elements.count+1)"; refs[ref] = element
            elements.append(["ref": ref, "name": name, "role": role, "tag": role, "value": value,
                             "actions": actions, "editable": settable.boolValue])
        }
        if let children = attr(element, kAXChildrenAttribute) as? [AXUIElement] { for child in children { walk(child, depth+1) } }
    }
    // Restrict to the selected application's windows, not the system-wide tree or menu bar.
    if let windows = attr(root, kAXWindowsAttribute) as? [AXUIElement] { for window in windows { walk(window, 0) } }
    return ["connected": true, "trusted": true, "bundle_id": app.bundleIdentifier ?? "", "title": app.localizedName ?? "Desktop application", "origin": "desktop:"+(app.bundleIdentifier ?? ""), "elements": elements, "text": strings.joined(separator: "\n").prefix(14000).description, "generation": generation]
}
func dispatch(_ input: [String: Any]) throws -> [String: Any] {
    let params = input["params"] as? [String: Any] ?? [:]
    switch input["method"] as? String ?? "" {
    case "status": return status()
    case "disconnect": target = nil; refs.removeAll(); return ["connected": false, "trusted": AXIsProcessTrusted()]
    case "connect":
        guard let id = params["bundle_id"] as? String,
              let app = NSWorkspace.shared.runningApplications.first(where: { $0.bundleIdentifier == id && $0.activationPolicy == .regular }) else { throw fail("Choose a running application from the list.") }
        guard !["com.apple.systempreferences", "com.apple.securityagent", "com.apple.loginwindow", "com.apple.keychainaccess"].contains(id.lowercased()) else { throw fail("System permission and credential applications cannot be connected.") }
        target = app
        do { return try snapshot() } catch { target = nil; throw error }
    case "act":
        guard let action = params["action"] as? String else { throw fail("Missing action.") }
        if action == "inspect" { return try snapshot() }
        guard AXIsProcessTrusted(), let app = target, !app.isTerminated,
              let ref = params["ref"] as? String, let el = refs[ref] else { throw fail("The application or control reference is stale. Inspect again.") }
        var pid: pid_t = 0
        AXUIElementGetPid(el, &pid)
        guard pid == app.processIdentifier else { throw fail("Control belongs to a different application.") }
        // A control is used at most once before obtaining a fresh tree.
        refs.removeAll()
        let result: AXError
        if action == "click" { result = AXUIElementPerformAction(el, kAXPressAction as CFString) }
        else if action == "fill", let value = params["value"] as? String, value.count <= 12000 {
            guard text(el, kAXSubroleAttribute) != kAXSecureTextFieldSubrole else { throw fail("Protected fields cannot be filled.") }
            result = AXUIElementSetAttributeValue(el, kAXValueAttribute as CFString, value as CFString)
        } else { throw fail("Only inspect, click and fill are supported for desktop applications.") }
        guard result == .success else { throw fail("The application rejected this Accessibility action (\(result.rawValue)).") }
        return try snapshot()
    default: throw fail("Unsupported desktop command.")
    }
}
while let line = readLine() {
    if line.utf8.count > 100000 { continue }
    var id: Any = NSNull()
    do {
        guard let input = try JSONSerialization.jsonObject(with: Data(line.utf8)) as? [String: Any] else { throw fail("Expected an object.") }
        id = input["id"] ?? NSNull()
        let result = try dispatch(input)
        let bytes = try JSONSerialization.data(withJSONObject: ["id": id, "result": result], options: [.sortedKeys])
        print(String(data: bytes, encoding: .utf8)!); fflush(stdout)
    } catch {
        let bytes = try! JSONSerialization.data(withJSONObject: ["id": id, "error": error.localizedDescription])
        print(String(data: bytes, encoding: .utf8)!); fflush(stdout)
    }
}
