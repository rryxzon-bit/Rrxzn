import os, math, random, struct, json, io
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
import trimesh
random.seed(20261115)
rng=np.random.default_rng(20261115)
root=Path('assets'); (root/'pbr').mkdir(parents=True,exist_ok=True)
# Distinct material families: plaster, masonry, wood grain, tile, rust and fabric.
colors={'peeling_plaster':(149,138,121),'cracked_plaster':(115,109,99),'aged_oak':(101,70,45),'weathered_floor':(87,63,44),'old_ceramic':(116,119,113),'aged_door_wood':(88,57,36),'dark_walnut':(59,39,29),'oxidized_iron':(71,78,75),'dirty_linen':(145,131,111),'stained_stone':(91,91,85)}
n=512
yy,xx=np.mgrid[:n,:n].astype(np.float32)
for name,base in colors.items():
 coarse=np.asarray(Image.fromarray(rng.integers(0,256,(64,64),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC),dtype=np.float32)
 fine=rng.normal(0,5,(n,n))
 noise=(coarse-127)*.20+fine
 if name in ('aged_oak','weathered_floor','aged_door_wood','dark_walnut'):
  grain=12*np.sin(xx*.15+3*np.sin(yy*.012))+5*np.sin(xx*.39+yy*.007)
  noise+=grain
  if name=='weathered_floor':
   seams=(np.mod(xx,128)<3)|(np.mod(yy+np.floor(xx/128)*23,256)<3)
   noise=np.where(seams,noise-42,noise)
  if name=='aged_door_wood':
   seams=(np.mod(xx,180)<4)
   noise=np.where(seams,noise-24,noise)
 elif name=='old_ceramic':
  seams=(np.mod(xx,128)<5)|(np.mod(yy,128)<5)
  noise=np.where(seams,noise-48,noise)
  noise+=np.sin(xx*.035)*np.sin(yy*.031)*4
 elif name in ('peeling_plaster','cracked_plaster'):
  patch=np.sin(xx*.024+np.sin(yy*.021))*np.sin(yy*.028)
  noise+=np.where(patch>.42,20,-4)
  if name=='cracked_plaster':
   crack=np.abs(np.sin(xx*.029+np.sin(yy*.036)*1.5))<.016
   noise=np.where(crack,noise-49,noise)
 elif name=='stained_stone':
  seams=(np.mod(xx+np.floor(yy/128)*34,128)<4)|(np.mod(yy,128)<4)
  noise=np.where(seams,noise-37,noise)
  noise+=np.sin(xx*.024)*np.cos(yy*.035)*13
 elif name=='oxidized_iron':
  rust=np.sin(xx*.041)*np.cos(yy*.035)+np.sin(xx*.09+yy*.05)
  noise+=np.where(rust>.7,24,-2)
 elif name=='dirty_linen':
  noise+=3*np.sin(xx*.8)+3*np.sin(yy*.8)
 albedo=np.clip(np.stack([base[i]+noise*(1.0 if i==0 else .92 if i==1 else .85) for i in range(3)],axis=-1),0,255).astype(np.uint8)
 Image.fromarray(albedo).save(root/'pbr'/f'{name}_basecolor.jpg',quality=89,optimize=True)
 h=noise.astype(np.float32)
 gx=np.gradient(h,axis=1);gy=np.gradient(h,axis=0)
 normal=np.stack([np.clip(128-gx*.95,0,255),np.clip(128-gy*.95,0,255),np.full_like(h,247)],axis=-1).astype(np.uint8)
 Image.fromarray(normal).save(root/'pbr'/f'{name}_normal.png',optimize=True)
 rough=145 if name=='oxidized_iron' else 194 if name in ('aged_oak','dark_walnut','aged_door_wood') else 225
 metal=135 if name=='oxidized_iron' else 0
 orm=np.zeros((n,n,3),dtype=np.uint8);orm[:,:,0]=255;orm[:,:,1]=np.clip(rough+noise*.28,30,255).astype(np.uint8);orm[:,:,2]=metal
 Image.fromarray(orm).save(root/'pbr'/f'{name}_metallic_roughness.png',optimize=True)
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
