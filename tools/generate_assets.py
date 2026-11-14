import os, math, random, struct, json, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import trimesh
random.seed(20261115)
root=Path('assets'); (root/'pbr').mkdir(parents=True,exist_ok=True)
colors={'peeling_plaster':(112,105,91),'aged_oak':(93,64,40),'weathered_floor':(77,54,35),'old_ceramic':(91,93,89),'aged_door_wood':(83,57,37),'dark_walnut':(53,35,27),'oxidized_iron':(60,67,66),'dirty_linen':(151,137,117)}
for name,base in colors.items():
 n=256; im=Image.new('RGB',(n,n)); pix=im.load()
 grain=Image.new('L',(n,n)); gp=grain.load()
 for y in range(n):
  for x in range(n):
   noise=random.gauss(0,11)
   if 'wood' in name or name in ('aged_oak','weathered_floor','dark_walnut'):
    noise+=12*math.sin(x*.21+4*math.sin(y*.019))+7*math.sin(x*.49)
   if name=='old_ceramic' and (x%64<3 or y%64<3):noise-=34
   if name=='peeling_plaster' and math.sin(x*.08)*math.sin(y*.065)>.6:noise+=24
   if name=='dirty_linen':noise+=7*math.sin(x*.8)*math.sin(y*.8)
   pix[x,y]=tuple(max(0,min(255,int(v+noise))) for v in base)
   gp[x,y]=max(0,min(255,int(128+noise)))
 im.save(root/'pbr'/f'{name}_basecolor.jpg',quality=86)
 normal=Image.new('RGB',(n,n),(128,128,255)); np=normal.load()
 for y in range(1,n-1):
  for x in range(1,n-1):
   dx=gp[x+1,y]-gp[x-1,y];dy=gp[x,y+1]-gp[x,y-1]
   np[x,y]=(max(0,min(255,128-dx)),max(0,min(255,128-dy)),246)
 normal.save(root/'pbr'/f'{name}_normal.png')
 rough=215 if name!='oxidized_iron' else 145
 metal=170 if name=='oxidized_iron' else 0
 Image.new('RGB',(n,n),(255,rough,metal)).save(root/'pbr'/f'{name}_metallic_roughness.png')
def cube(x,y,z,w,h,d,color):
 mesh=trimesh.creation.box(extents=[w,h,d]);mesh.apply_translation([x,y,z]);mesh.visual.vertex_colors=list(color)+[255];return mesh
def save(path,parts):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 mesh=trimesh.util.concatenate(parts)
 mesh.export(str(path),file_type='glb')
oak=(95,61,35);dark=(48,31,23);brass=(181,142,75);cloth=(118,71,63);ivory=(186,174,153)
def furniture(kind):
 a=[]
 def add(*v):a.append(cube(*v))
 if kind=='table':
  add(0,.91,0,2.05,.13,1.15,oak)
  for x in [-.89,.89]:
   for z in [-.46,.46]:add(x,.43,z,.12,.86,.12,dark)
  for z in [-.44,.44]:add(0,.68,z,1.8,.12,.08,dark)
 elif kind=='chair':
  add(0,.48,0,.65,.12,.65,oak)
  for x in [-.25,.25]:
   for z in [-.25,.25]:add(x,.23,z,.08,.46,.08,dark)
  for x in [-.25,.25]:add(x,.87,.27,.08,.86,.08,dark)
  add(0,1.16,.27,.58,.32,.08,oak)
 elif kind=='sideboard':
  add(0,.81,0,1.6,1.55,.78,oak);add(0,1.62,0,1.75,.12,.85,dark)
  for x in [-.5,0,.5]:
   add(x,.81,.4,.42,.85,.055,dark);add(x,1,.44,.06,.06,.04,brass)
 elif kind=='wardrobe':
  add(0,1.13,0,1.8,2.26,.85,oak);add(0,2.33,0,1.94,.14,.95,dark)
  for x in [-.44,.44]:
   add(x,1.15,.44,.78,1.94,.06,dark)
   add(x,1.15,.49,.61,1.77,.045,oak)
   add(x+(.27 if x<0 else -.27),1.16,.53,.05,.08,.04,brass)
 elif kind=='bed':
  add(0,.4,0,1.8,.3,2.5,oak);add(0,.64,0,1.68,.24,2.35,ivory)
  add(0,.8,.25,1.67,.1,1.65,cloth);add(0,.85,-1.18,1.8,1.55,.15,dark)
  for x in [-.65,.65]:add(x,.81,-.76,.5,.12,.42,ivory)
 elif kind=='door':
  add(0,1.17,0,1,2.34,.12,oak)
  for y in [.48,1.35,1.93]:
   add(0,y,.07,.84,.065,.03,dark)
  for x in [-.4,.4]:add(x,1.17,.07,.065,2.1,.03,dark)
  add(.37,1.05,.11,.07,.07,.07,brass)
 elif kind=='flashlight':
  add(0,0,0,.16,.16,.48,dark);add(0,0,-.28,.23,.23,.12,brass)
 return a
paths={'assets/models_mobile/dining_table_hero_pbr_orm.glb':'table','assets/models_mobile/dining_chair_detail_pbr_orm.glb':'chair','assets/models_mobile/victorian_sideboard_hero_pbr_orm.glb':'sideboard','assets/models_mobile/victorian_wardrobe_hero_pbr_orm.glb':'wardrobe','assets/models_mobile/antique_bed_detail_pbr_orm.glb':'bed','assets/models_mobile/paneled_door_detail_pbr_orm.glb':'door','assets/doors/the_house_basement_door.glb':'door','assets/doors/the_house_entrance_door.glb':'door','assets/doors/the_house_interior_door.glb':'door','assets/models/flashlight_pbr.glb':'flashlight'}
for path,kind in paths.items():
 save(path,furniture(kind))
 b=Path(path).read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<I',b,8)[0]==len(b)
print('Generated',len(paths),'GLB assets and',len(colors)*3,'texture maps')
