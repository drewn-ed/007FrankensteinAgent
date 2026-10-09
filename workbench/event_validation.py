"""Independent showcase checks written by the team, not a generated capability."""
import csv
import io
from .model import RunError


def source_roster(inputs):
    """The documented showcase import policy: first valid row per normalized email."""
    for file in (inputs or {}).get('files', []):
        if file.get('name', '').endswith('.csv') and isinstance(file.get('content'), str):
            reader = csv.DictReader(io.StringIO(file['content']))
            if set(reader.fieldnames or []) not in ({'id', 'name', 'email', 'first_choice', 'second_choice'}, {'id', 'name', 'email', 'first_choice', 'second_choice', 'group_id'}): continue
            rows, seen = [], set()
            for row in reader:
                item = {k: (v or '').strip() for k,v in row.items()}
                item['email'] = item['email'].lower()
                if not item['id'] or not item['name'] or '@' not in item['email'] or item['email'] in seen: continue
                if any(item[k] not in ('agents', 'design', 'story') for k in ('first_choice', 'second_choice')): continue
                seen.add(item['email']); rows.append(item)
            return rows
    return None


def verify_event(after, before, inputs, preserve_unaffected=False):
    if not after or after.get('applied_revision', -1) is None or after['applied_revision'] <= before.get('revision', -1):
        raise RunError('No new allocation was applied in this run. The showcase outcome is not complete.')
    expected = source_roster(inputs)
    if expected is None: expected = before.get('participants', [])
    if not expected or after.get('participants') != expected:
        raise RunError('The imported roster differs from the independently cleaned source records.')
    people = {p['id']: p for p in expected}; workshops = {w['id']: w for w in after['workshops']}; rooms = {r['id']:r for r in after['rooms']}
    seen=set(); counts={}; first=0
    for a in after['assignments']:
        ident, wid = a['participant_id'], a['workshop_id']
        if ident not in people or ident in seen or wid not in workshops: raise RunError('Invalid or duplicate seat assignment.')
        p=people[ident]
        if wid not in (p['first_choice'],p['second_choice']): raise RunError('An assignment violates an attendee preference.')
        seen.add(ident); counts[wid]=counts.get(wid,0)+1; first += wid==p['first_choice']
    for ident in after['waitlist']:
        if ident not in people or ident in seen: raise RunError('Invalid waitlist entry.')
        seen.add(ident)
    if seen != set(people): raise RunError('The allocation does not account for everyone.')
    for wid,count in counts.items():
        r=rooms[workshops[wid]['room']]
        if count>(r['capacity'] if r['open'] else 0): raise RunError('The allocation exceeds available room capacity.')
    groups, destinations = {}, {a['participant_id']:a['workshop_id'] for a in after['assignments']}
    for p in expected:
        if not p.get('group_id'): continue
        group, destination = p['group_id'], destinations.get(p['id'])
        if group in groups and groups[group] != destination:
            raise RunError('A group booking was split across workshops or the waitlist.')
        groups[group] = destination
    if preserve_unaffected:
        old_workshops = {w['id']:w for w in before.get('workshops', [])}
        old_rooms = {r['id']:r for r in before.get('rooms', [])}
        unaffected = {wid for wid,w in workshops.items() if wid in old_workshops and w['room'] == old_workshops[wid]['room'] and rooms[w['room']] == old_rooms.get(w['room'])}
        current = {a['participant_id']:a['workshop_id'] for a in after['assignments']}
        for old in before.get('assignments', []):
            if old['workshop_id'] in unaffected and old['participant_id'] in people and current.get(old['participant_id']) != old['workshop_id']:
                raise RunError('An existing reservation in an unaffected workshop was changed.')
    return {'unaffected_reservations_preserved': preserve_unaffected, 'verified_constraints': True, 'participants':len(people), 'assigned':len(after['assignments']), 'waitlist':len(after['waitlist']), 'first_preferences':first,
            'checks':(['Group bookings kept together'] if groups else [])+['Source roster matches', 'Every attendee accounted for once', 'Preferences respected', 'Available capacities respected', 'New allocation applied'],
            'scope':'Showcase constraints only; not a proof of optimal allocation or all user intent.'}
