// Keep in-flight local edits when applying a server snapshot. The server detects conflicts.
export function reconcile(base, local, remote) {
  const result=structuredClone(remote);
  for(const key of ['projects','chats','workflows']) {
    const before=new Map(base[key].map(r=>[r.id,r])),now=new Map(local[key].map(r=>[r.id,r])),next=new Map(remote[key].map(r=>[r.id,r]));
    for(const id of new Set([...before.keys(),...now.keys()])) {
      const old=before.get(id),value=now.get(id);
      if(JSON.stringify(old)===JSON.stringify(value))continue;
      if(!value){next.delete(id);continue;}
      if(!old){next.set(id,structuredClone(value));continue;}
      const merged={...(next.get(id)||old)};
      for(const field of new Set([...Object.keys(old),...Object.keys(value)])) {
        if(JSON.stringify(old[field])===JSON.stringify(value[field]))continue;
        if(!(field in value))delete merged[field];
        else if(field==='runIds'&&Array.isArray(merged[field])&&Array.isArray(value[field]))merged[field]=[...new Set([...merged[field],...value[field]])];
        else merged[field]=structuredClone(value[field]);
      }
      next.set(id,merged);
    }
    result[key]=[...next.values()];
  }
  return result;
}
