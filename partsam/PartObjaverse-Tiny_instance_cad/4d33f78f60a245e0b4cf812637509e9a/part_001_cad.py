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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d33f78f60a245e0b4cf812637509e9a/part_001.stl', 'relative_path': '4d33f78f60a245e0b4cf812637509e9a/part_001.stl', 'source_sha256': 'adf5cef939811b385623986e57262d1621593902a5288f834d164075e1bfaaf7', 'input_faces': 348, 'input_vertices': 255, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.02918737754225731, 0.3552580177783966, -0.08179304003715515], [0.1025802418589592, 0.4062395691871643, 0.14192736148834229]]}
GEOMETRY_BASE85 = 'c$}r03sh9q9>x!1Sw3#2;3Fd^HSt|3rfJ4#nJGTV5bZ^yhzh1C;0p<kFHls1Oq5g@L-Bzipn!t|95ho&5fM$WaH6h8DVipd7T*2%rc1~FUF)uUXRUAjzy166+4G+>GkfL?czQTCbyDQ*StakAzG<^MC<<3g#YtJ{7Zl>}>lfT_?z|-qN^8OS&0aT*pES<%9S3Ehveb3DU$AeG>kxzMD>DYW_A$852n-4dnmYHxz@X`VoWC*kqhLSAgJ(^h=f}o9`VSn~$1tF0AH&Cn|MAwGwV-+Yu+5!S^Ze=xUey=<t?mRjuBt4gxO#185wFU;-brF!`2#sWVTzUH&L;{fuAbN;)-koXk}UXZv*i4s4cQb|y0^4YT&q}VCHdK{G(XZ@qqzBnujJ#Jy?TeJCsxV(owhog;@YqWhbXRgTxccvlQAUMq8&7fo9nHjA9X|7PF`)MKso>M6f4Eer;5dVTSjn-cziq8$@%j)T1nphQH|o}&x+)EF#fPh<X!Gv<kheu_Fy5wO{3amQe0`@BbDNschz2U{^jqJNnTo<Kyl-Z0KpCV`O1%xBo7@l-JRm$FU_R5T5vg*<Y^ZZ$#rVolPGSSyETQJe`RwT$uFD`+^9cqDbunju2$Q!$@!J_BsaEOWTCh+@s5?8Kc-baIsfQLjp8<2(<6dUjM^>wTh(5?t_)q*h}X|Uys%{^#f{BeQYmh(yRetyN<?KcxlZ8G1d3}hzJi<d>)`eC5D)po*PY^__h(RC^|=^J&cA*#k(__JXA;GY>FZM{t}Td6BiEmiBe<%cA3r&Z;%eFXY?2pWC%Lg-fQ919r&p}x{OAUfD~pC{WS_h5%l#+Xdyja&9S6$!9tHUnH{A4*`(#bM;HK3R<@^I_`4l(o@RsXWRPGgg+8y~miZ05gxYDG+O7eT>Nv;j9k)LY~uBl?(Zt`*2yj|tzPTf+$m0fM*`T62tHpP{y{uYvt*l#8IkmDrRN}eU}*L=+;`ZW3<7u>McP0nxLS<E*?)$J4cy$JbuTkTAwxUt}a6pCvj{p3ETpKsq!^y>$Y)+lcCY9aO$4f~}ne4Bi}&P){hhE2znaq*(hhj_zy(Wi1%x6Uf>G>RLiDftvvT!(8Ew>{=4`c%&Pr;B<iPo9U_WjW&ffE(<*^>>FUZX8-G&ySwZ3zM(&)Sm^{UW}65F<tDd5Aji>Qz>qXe6W||+6`L*#nt^wNUnr*^`rVx7I&E?USIlku)pcKlD<Z8P2c~Ob7>@xY?e-ObxeyKifbdfl3e|wPd>>%f1TvYlilU>8{T}sIFHLN%K7gd&!M>1qx3Mvm8F;SDQ@Z(BKM7U(Sn;c?~so-IYmCdI&Qk$C6nTYtHV<%u63{9OL1e;&18xzpHw7J{IA!8e*W<DktARIllb2C5D&XLlj3Sai#U>}wM`<|i3ujTI=)D}-_82@-H)YF+}Q38$(0G=SrpfXC^_W(0UhM)O+UYGi-qFGYL|SHXAL5`;mrFQ#g$_&^7ZM`IYZQ^u#crow@_SZJ3{Vb`vL`5eX!3IOtw(m_SMVsdLhY}Dem{nv9g~~>w!XoYc*bJ6jz*`_mJGFdK<}8V>Xg}tiKoMidn}!2ZXs3T&?liLUCiy^6eydt52o4>9^Jy6xV+5l1*`?d{8dgPsL~}xy}Kf0&@PmT={uDDOPZ$cYy5kR*pFTdTw4bE{)<!cB?%UHyy0pMsama)JAfhDVM!SUg8`^^{MuJV++}T$CKjxoAm31)TC0}Xl<53akZv>HpR80eR9clIu5mx>)f7DKyh>H3~~Mqfz8Bzpmb`5&$Ze_ifbdy^81f|{*e*+6j#!E$?K*bedTrDgMRXPc`#UBAL+PS_~;Ib+xKCUetx36*jM#jd-c~8iYw12XOZ)-d~Kn)ap+R{{jHn4&M+_QCGXewro8UcaqY&eOp2?c3dQG_NzZZJt>?zt@Dz$Gk#X`mNWV@Kw|t5lcKK)&w~g&8o)`7IFu`qpct0*0AU}U~-1vm!4vPQv`KVu~>V-IJeXZXW`T3<^=Waq4#nlU%h2n-w!Sefj@%jT|UVPLyVx7fBz9g^8i>0{Qw=R+5+P%>^Bu}ZdkUZ31oPSf)1;Ne7%jEr9BDYgq8;~!rqjX$#e6N7yZh7K;s{LLixS`Wdxqe8bFUg<T7fW$<&ecSUYe$SZB#%F1A=e4;5s%l<&h?<EEpG~Ls%#MZww`MVC34@^apj!|aef}+A?c|US38X_AbEL~{GRE1OmI`fLBWkx=_&I4s^fTHE4Q4*{%RY6=Ot>1c>No6TrEkK*Ms27Ym(bvho%`l#eQtFI?4VQ22Ce<%wYMwPREUx=H^gb3rLXX`OXr#-#he|>)3zy16RTA*CTqaB>Ux%+_m09ac%iJdB36Z_h8cpl@~;xAFarxxE7Zxe{bL8DZgh`-<9*-LUSpuEi=pCPyW0m?|+?D&d)XEiN~KcLR9mu3c;0#_Id7}fBP#%@vt?XrL7f(>v6?NnK8A|pC~xwH+!Z3MB(rDU;T+<fZO2z_fHfbupYi*I)-`$p4aQ}U!wjK^*a2EOdXlRQT^dxVCsOp12XR0BYPgc1IA%Yv%qH|<9;{OX5^cZaetc0irk8f`#nqv$P<vAMqhi-n?JHW=*iyi^No55gZ~&c96lV!eT;e<J`8m?>S_3=nU*oR!OzCH6W9Rwr!nr&^c470$hePS3P2u!jQhPzpCkVq8TTbj`N;E;ai7Yx1^E_aCFp53^4Z8z(bF>Y(7#bH5%4PNGWcaUPDL$&k3ijvS_0phX(iJj_&FHA#PkgKGsw6f$mD|D1sV4rAzKdbg7H44t>9acaes!X0C@p2?$emIA>W4V40@V_d=9cS^knaMAnJ06`xU4w;aB3g6{u(6m!s}OJp(_4sS8sSY9Rc}3g2dA{wy-?2QwLv8<2577uhO!1IFo0iQtLIxG!ZYL|%xD`~6Hw$dizjqNhOQfynlwCwsqxQCC6SN1{f-N8z|g)Kd6WsOhMs@Fu2rm`<Wv;6G%Vf_w@x?tPdhBcF_n`{PW9kRL+E{Uu~q;SXV4%k&HQFUYw6iRoM9-y*9;PZs1BWIv%Nd%r%7dN~e%0`(;PNgQ_qwHE$3>Q&TQ_+d=XF-4=!hwp~$75L{c?g};(z8l7?ndX7dL&kjulNq@g8TV(IG~^mG?lYOTBj1kfEP9%cd_J;F^c3BwCwnie;n$!>!$;$|HK=FdSEFX2o`p9u^<Y|$8Vv7>%pJZ5#@)eQg?GhxEmIJ95Hjw+K$Zm`gmD>D5qJ?Y?hh~}BTq(FhMt0v2O~Rxp4K<&$==Ia_;sl3;n(B1b*N?VYf-aM%iv#Q>dh33x&XcxvJvpTG42UA9KILEF-#%gA;`Gjf$SiB2*&4_j({IQ#(g%^PUJh0okLFxkS{=%jh<o~^<?iQ2L2P&Sol~R_X+Ab_!!iKsORAS!Soo@MAWhHt(cl2Z-$KfN0GIJZ-%ialLxp5GVZ4%TMX}kaXiy!;GZGmehHHwazAA8=xHqSvB;L7Cwspw8};G|{}$>*_=z~~E!22;Pt?Vz@$io@HDPLp+7`YklLK-GWZXL{^41j90iJ)gZiBoHGVVtq8x7wEV{fJj;1iH>KZfZ|<ZmMLMo(>#w?#GvJ=yzpY}AVryfbP$_;xtX8Pyx!33W88H~f=KEtn>uj)!lKtTlWKj2{Pk0=_xMZ!?VpABT+l8OTE6$6>sQX(RYXWZW-hnu&ZSvQ6k|Jo53#mZGOgje4^8@;1B|>LmC{IL-@o6a3q#p{SeSeVN{8I)!=|{yk*V;NQo1D$~2*?;_*Am?;l=9y0E~LskQyhw%-jYv9+AasM+@74j-%H_+2z<cE>{jGj)RhpCNvDTe<V^%VRm9QQTq4ftZz8q^!`Z!q;^+JL$Uek4<0<b9EG-v`<2@O?3kV_FEl5E=I=$a3HpVqDI26#OVM?sJ)TA>W0p96c>Uz6e<^db0QXdZS+A;6Fv(0KWmpeTrHRABUQQS`PmsQzcV9>TUQRm@1H0AmhH8=_2xr$hfa#x`q4}GVXszb|3y0#tlq=g8zw(`#+fOA-{*L0X^MDejC{z=*ix1b)#PD;P0Z=!`I`uyQmHDb*T4I8{ofTy2JE6{I3|>m@a@{K*s%Lrt`?pBjf%ivfr3IJsg@iIsT`A+5GoS<(vE8{()0}<llcrX?$b~TkEeMRXjZ&;h&f6L!^oP63M?^DE|VibB-S'

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
