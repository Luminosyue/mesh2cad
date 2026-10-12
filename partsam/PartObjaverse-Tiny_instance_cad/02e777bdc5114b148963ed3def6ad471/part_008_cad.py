"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/02e777bdc5114b148963ed3def6ad471/part_008.stl', 'relative_path': '02e777bdc5114b148963ed3def6ad471/part_008.stl', 'source_sha256': '464d3429bee9694cc3cf34707da99fdbaf3d0e87675f6ad59f4170a63f783064', 'input_faces': 260, 'input_vertices': 150, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.006399037782102823, 0.3953869938850403, -0.005768755450844765], [0.026908574625849724, 0.41560953855514526, 0.009914491325616837]]}
GEOMETRY_BASE85 = 'c$}q~2~btn8OIOck|;(+3~tdIfq)A{P~3}G6j2bw1qBp+>>6e9vAE!JK~Y4J_dqOa7iya{X_RaxHJe;Bjbmez#yB-GPLemVH4~e~)?}KvWct4E{4ejGPCL_S-^@4v-~GSup8eeO?!5GrfF8j@ejXOnC%oJ0dO!$@KoKme3!Rng@(U}XOUt+Ti2>}>$I{lcjMVfjKT$1eA_@vC@|_XWwTPKTQzOP}5k+OrN@s5AnlfiWA^G!iH&hgQ{ff1@<%Qns$e6eZ<F$!n#%tTP|MAnu+k_5J+}2rMHP0{qkks>3az0;=C{TRuiTBG%^^mq2)-{vacXT%9+kGQ;lj0i(&MNu()yK>2zLjtJTK`cyNJYbN_RULv1$JNW)uQ-%P?D0b=Pf9=`&NFpzwEMM@0amp)Ed5j<adg%y|Kv2{Rq`-*}oYh%NaIS=6{*1`nMA~-^@GAzHzvQeX;F^gTH^}1;y7BS~qe%BCn3~!h&VLzV4OF*VlI_zSdUG`Qo`#?3<ZKWH~tt^Y}XKZN=~S=uPgg<FtFXy<g^m->=|uUVV{$y)H_&vnYXm$Is8G`Df2p@VXduP0hb|UHa4V>iPQd9kM;GhgQk?-=p}VsaB59=2PsO`9ZS$kRhC}UA&_Bj;Gr>-?KJr58uD}kesj24)b^#Y1NAF$xM*rvvgbofBz4(b6#f}mv=C=!QL-XUYO2#Ckm8&eZ<}>F0XU9lCOQNvv2&Z*FL_#R<1YW?8xPOJusSmGfA#z5xq=~b99`NZ+_Ip<K{S?rR3}1l(KKM{2=`a2V^-L&*gCbjZuwuU%&af?C-bFG%Ef5Vpb%#Kl)6g(%%Oz#IS$+j*@TQ&DzX*r}ut)zP|h3CSFIM1n#%DU)-pi&v{E8+OPC?%!?`9&S}X?zE;ztn)CcJm3+_BM|nK83sw7-{?0tc<EiP#72l}Mlk2T_c$0k{8qbR*UF5Hx-eg}t;_1g`ldreWZBoX;G&#THW=WH>J{t}uk}rO0G}+gcNWVIQe8(-fQm>wqy`9VbS-VoNcD$E-u3dRvt@ow9oNuK5QK{E)zFy|1UQ+7q_(|dxzW%tlnbmqebUvBG?Y!66Y~Sx9WMVe?#;~K($8*X2ye^-|q4^B^*7K+1;Hg~lHP>6sN;_}dDd6!8_)M+0poe@uX5VdA)?s`^A<s*czsuep{dD9`zW=oVmy&;{=LR09M}uAVb{ear<nysU)Mam{aGvIRJy)Y$_I4V#8aQ7+x8J3#!@f7=c{HL`@y(t7CH%eL6E0;vhyIrHJ<TT-U*8qW`HmT<UCMe$l+P2R^DXJ)+;PlYxUS3QTj!4Dd$dbRImX5IO4-leZqCQ~s3r6+?XvmS`Pl7$Im~UZSKO%Q=f34z^;&+%#Zb3>+|1Lz;Pb-MC(^C#mtTF5%=z0Qm3(nIxt#Y)M3my|hk{D^`%7_dWgi*W6S@4ar_1(R&(*KW<T<rtu3B&L-AcRP{ao5QgUi>FmMP_XM7w+rk6WXRn=U$c+5PU{74RJcoNi^mES;7_{W1scR{CWGrpfc~%yA{(@pv@v(~jWZxb6Ewj1F7C`>RX(-REQ6_1S!X>Iro`<3Eh&el)zL<U76)@;N#2Z6#kDw@CVvt}69<${gGtbBM=n-!Den_ltR7I|sMeee-PRHoh-oSc|gnp8TGlhmMisTkPvf_fO8Z``y2z;G3>VEy}okawUV;c}u!dzGuocuGgGZqU7s=ZSwgU>Qw4AW`1heeXCx}cZ4^#*yr7dt0?ZW`PRH!z9;Z?rCyQy0`EujPnVT)9A`h3zvtk0|Bki%pnk3PavaqqyuY;gIc=QZT6cxZYgt=H<%{Q@mwwnz_Ko-7bMpTE-7C_6H-mk#_F56=uOE7t?|)~B%wG|=f&2A+Gy7uH?JIKMv{!QegWt;hhq7fkFPkacuh!erul<gFN8hSVTyK2ZkJ+!;C-c8LJBRa&USnU>XG%Z+B`(K!b80(ZKeJc*2`4#U?_J2g5mGA0dHNqJxSh|Iv9I?`ljHD4EVtkM%dchrsvl%IwW%xFU)d?k4?sC5FI929*&oRK%0+S<-t+MI=n0#TaJd)S<-Qm+jmOhWtYcs7x+n8bEaCEvzaM7b+`Nf>E#Y0x@A&waGXI<`$6Qs(?bpt|D)YNa<oay!m-BME*HO-IlKIAmV@tTdSwZaU+7?;w6DxV%%~{K&??yR0`g1wj#a!uEpqyi|T#jegsiSfn(Vou_aC;2#XZFo-={qhg=k{wydLHBUJatRfd%J_@S06e{`tNU$<uCq$$I}x~eN49J8_xH{p6B)B`D>H(-;nvD&)tfybmeV!-o(pOpA8g(;(qVjY*DW5RhCTpSo-f@W!FvmuU=(iC;#8CvMt^=?4Wiai0h%-!1drd=x#9SesCT50D`y~dJx<Ub|Z+}pbg+Q@F8d|_z<|s8+)Jzv=(fDw?lV=NjHPHgSSGrfVYBcp!>iz;9a<PE9%*b@2q-j(5@Qf?t$(D?*TVKTfj}=L(o=Re_L&1(rOzwVi&X?>;gAJ>%eY&*9>j6%|)YazKHii>%evRj=01d1>SfJL7a~u&Vnujldb?~fmeE?%p0ZND1sJ(3-NssbOpEwya2ikyZ}5OS^%C8&V-hLGr?=UQ30)lmVhh4PUvG`CwM)AI1ic+&I4y4h?AjN;4Jhl89|%^Ed-~4vk}C_&{A+QxEw)T1uX+tfj4=h8oCZz23`kV1uX&>VSHC1i04A*gXe-1pqbzV@InOf8t7W^8t?|&d=RHW7egz+i^0pGmEh&zbf^=Y4o-!x2d~FGr6P!DB8VqKGr$>`r-=yS@d)D42;wkk3OEcL4b28egQr4^!BfGrq2=J&;3Wv+9B36d2kd}u0z1H~g>N0KMi4JW5O0L818)T9LRW!v!Hb}C!8CV2!n|z&TXRjk5IPx5Izjl>2{Emmq274V8{yE0!KCBB;owK1)4-(D!H<Gt5X3VO#B&hD^AN;I&}rZ#a3X?u3W9hnbR2jb+Bz0NtU(_HYv2$BaX$ocU+7S9UvPf}@gM~8LkQvsXgD|=V-W$30VhD`LSw)&7$a+s&%pdH0_Q^KfHy*yLg#?zU`(wwMr^G;Vh1!y_|__M4m45t);6)V{)uNprwHF3A-47raWr%+cr3=<+JnSl&=BF<v&6#@!~>!IzyrbeA&7fG`+|Fb{h<B9e&C)6;`^b4z`dbC&_UoqnByP>@dyO*BhU!2HOG%YCxGd{3;L-_KR<_gV}LgXLj%Eq$Qg_v9tj-<CLIGF366wL0!M;l5ybHbV%;0FpmESi;5cv;bPRY5>W)GXheCtFq2M9VKHwo>`WGnxDxiIY??dbl4FvmxdqD?)?}HA64iLU|LOdKgO!(Fnv9;caM?(jL2V+b}LnDRntRWr`jTOH0h}b%(h-X6Mh3||bw$47{bf_+T=O*!T+uT^^EHRzK=_!8x!2$p2uRGtzpvA8Ik@v56s;^1*JKyn^)&0_xp3;-X)jI+H{IGeMMo|0{SHwJX'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
