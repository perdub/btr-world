"""Read the standard NBT tags emitted by the deterministic statue generator."""
import gzip,io,struct
def read(path):
 f=io.BytesIO(gzip.decompress(path.read_bytes()))
 def number(fmt):return struct.unpack('>'+fmt,f.read(struct.calcsize('>'+fmt)))[0]
 def string():return f.read(number('H')).decode()
 def payload(t):
  if t==3:return number('i')
  if t==8:return string()
  if t==9:
   typ=number('B');return [payload(typ) for _ in range(number('i'))]
  if t==10:
   result={}
   while (typ:=number('B'))!=0: name=string();result[name]=payload(typ)
   return result
  raise ValueError(t)
 assert number('B')==10;string();result=payload(10);assert not f.read();return result
