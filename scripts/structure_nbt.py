"""Minimal deterministic standard NBT reader/writer for authored structures."""
import gzip, io, struct

def read(path):
 f=io.BytesIO(gzip.decompress(path.read_bytes()))
 def number(fmt): return struct.unpack('>'+fmt,f.read(struct.calcsize('>'+fmt)))[0]
 def string(): return f.read(number('H')).decode()
 def payload(t):
  formats={1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}
  if t in formats:return number(formats[t])
  if t==8:return string()
  if t==9:
   typ=number('B');return [payload(typ) for _ in range(number('i'))]
  if t==10:
   result={}
   while (typ:=number('B'))!=0:
    name=string();result[name]=payload(typ)
   return result
  if t==11:return [number('i') for _ in range(number('i'))]
  raise ValueError(t)
 assert number('B')==10;string();result=payload(10);assert not f.read();return result

def write(path,root):
 def string(s):
  b=s.encode();return struct.pack('>H',len(b))+b
 def payload(t,v):
  formats={1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}
  if t in formats:return struct.pack('>'+formats[t],v)
  if t==8:return string(v)
  if t==9:
   sub,items=v;return bytes([sub])+struct.pack('>i',len(items))+b''.join(payload(sub,x) for x in items)
  if t==10:return b''.join(bytes([typ])+string(key)+payload(typ,value) for key,(typ,value) in v.items())+b'\0'
  if t==11:return struct.pack('>i',len(v))+b''.join(struct.pack('>i',x) for x in v)
  raise ValueError(t)
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_bytes(gzip.compress(b'\x0a\0\0'+payload(10,root),mtime=0))
