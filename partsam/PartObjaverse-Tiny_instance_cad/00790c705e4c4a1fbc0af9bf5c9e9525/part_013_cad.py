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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_013.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_013.stl', 'source_sha256': '745d4153c18385cde807af64fe01155dad4b9e45a271eff08ba0770e91dd4278', 'input_faces': 224, 'input_vertices': 164, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15790987014770508, -0.2080407440662384, 0.15541189908981323], [-0.15001481771469116, -0.19898495078086853, 0.16150063276290894]]}
GEOMETRY_BASE85 = 'c$}q~3sg?&8pn4^A<9q<!)S}?LK-S1Nn1h+MMQ@BK3$YjbX6)_Qsh=bxn(ylC&n<dEat2^v&MF^W?W{S%M522j`?DW<35ZL$Bfgr|Nk8OtaH{n>zr?`Z~cG%o}Tx4pLf6S_x2SPVQJ+c;5AVAX!M#Ylf59A-`xcVAulN_Cp94{+bd&9frZdh^Ubdgt(i7!YE-O+kS8p6OH9g6$Z{Jkx{XO5<>o26C1+;kWEnH!GqVzt%>G1UdUjH~pPgb{lGOfh_Yr=+o}!P3r&uihkFRd#8WR0ZpKKSo)0^kasy_8Q9c(VKWTfV+-#Tf&bkrYyxv%D%4#PLh9Hse&O+K2hT(i=AQ`G?YkGwVCVA&b|8E4Ixe-B@^@z8vsV7lfjli^EVh*y6SHD5SC0)B-%#$AVa`P6XavDW)i-B65s`O#Tz+@HH5PY!%x?qkiD%WO4Y4T3LSfG=40Ks{aDk-u)VmS4G&rukxs8~if?s51<{oZ*UoJ{pDiy^E0lp$PxhbuGWT=$9rfz7f8m7kv5j-!)&E1YZhihCleZ=9{ve5ML63`CeFsK0Cu#=Y(V2Bc<rWIY-SG116)+qLqlZhi_{5TFWmcKSDiW4#;2nXU#W!{ZRA8%-+bq;7_PO^nvC}ZC%jMs3z38>kjgqvq65-DZ~fg)_kGb8u2Bn=1UK5A<vgDn>2sj9IZ|{U<>-61z&s~i|6pmtysrC^b_90e8Xzd|F3>Qo*~DPKL+`Qm=~Ha=O4rRj=u^2!gI}+&VP(PgtcnE!3bYyM*TwT5Y%)3S(C1Qclc^9e5v0_%y)?g>X|@)=tr8b#J3>-oi<%P;`x49uaGufJ*N9_A&(#YSL@<72IJm)+VuLm2p<MweLsOO*B-&Tto;GwZg{GzN9}|B0)091kBIj~9+S-z#1|hx{ycl+_xefmP3euOb07L?aH3zc5Bay-A;0ru%~wvm5C1Iom$>GUF28sa{Z}i0Y<hiPh(*)TA3yjV`$CF<FI<198`l(wJn}{Oa)}9f9GK_Q1FYlQJJC;DYxH^K16`fsQLLA8=sxOsQHOP$)ERwPa}V(?3g+dDc(n+=bblNAR%L~87v9BsP2P<<_v86Ag}|5YZh?Q>66<^9wysWP1meYX_-aix#vS(({kQuY`?Cpo8h=F}e!hi1uzukxpZ^bTBEIVe^wS0LO3+PR{Yo9;l_{<0!(S?q=LpU*!3w_caWeL4aRb)3wFPxX^Sq5QU>~h((al#~jQmnT3-|k4_;t^@AK`bL=hAZKx%va<m5_pS!(%VcJ@`UA;*|}Em!95$Us-|t!<qk6_$J3i$kVhB&%f;rT|Ya{F*WBpeAm^er}-K3<ToQvVHx_L_!Rw#Zr1g=BahN%Li~57h~JGo!j13QpOxsdFY+jdzt{JF3hTLZO+T;i?xLRu;Tv3#NACLs{w&7ltw8;b$glRgrmJ6Y#W`;X{;O`jhL_Cm24C$YqkfOasJ|<GxuOK|y)mx*@GA0j)Fb_fale8ub}vRf_NYfpzN+hk8jgB|{a18-lgHeHzY@M`L>@y3>Jf7p|Lbx*56-B^6n;flr<8_z+8e0rkFW;g%6Bg#zO(@Gp~$1O!WX|O#JJgyd2U?RjVm`YzxQR`eC2QXc^Y>K^~WqjohR5&mrJ^Fg*N0dlwHL7cHFPrm*70yegWqa?_)|Cd{e_WsOK1b@elB&xO1o{BOCXz<Bix~sb>(Mkc<0<-yxh!g<oLYsrm5te1JRwr%*rdji&q}oU2VIQ9tjQLMwcA;^)XSjQ7uR#fU$51nXX1g8VNJq8^9CSeMUb#P`Cua^WGw^L}WWS%&i`?I8P5ihbSVFwSjbBkJV+Q>sV29CiSGD5ZZ9zItN|;vZBXkM{w@Ki>?W_dp@B0^?R!vp<!n^8n(N&??09K53edcr|h({q@NI0`cP34e(O}v0ed;zgUcUC2m4|c|H2StO)VE2dd8Hh<7T)I-066uknai{R>bh?~_8!YOZ@8`Y?M7`ro`8&y^*7Q|%NyS2x+`xJAfw9`V8|+}{idDZ2Zcuom}EAto8?m0SzIv<Ci(MBTkkoG+u#ix*(r``c0fyv>;JKqH=qFXr)iSb=$cG8g@MqYnK!z83MvX6rsLOm@o=Umb(K{dNcH`2~G8oQ>9fE|`J}5Wi{$;$wH~`Yg3YqMpyvQ0KIK_>aSN`$(FQgZb`<FJ0ORe-NI3sb!*Wf62{D(T6JdQb9fH{IC%IlMvK1ya091$wd9XfiF2UAkW}sh@TOno3HALdL(!FBKMb}Ap_?|=vdu+4I!+@Zme#9iB0_dC_YHPz7H4Uxf%pt=Dtuu5HB<Y^1hAdQ@DrUn?&Pi^x@VX)E~@x2EZ4dm7#BH3f5(MfbKaFK0_YKK0vp>1V_Y6HU7HiTu~MxfA&b!zjPP+lL=oP3SYRk5%Fgd(TAfx@PD@r{SR#SqjcX6d|KgMBG|TL`@5^)AS4@K`)WY@4?%dP|Ng6iRNw#Vs{wEC|NE<fciU?SY<~w(L&yPSi5f+g$Wy8Bk*AVpQ5TSBk>jb!<alxdbs;%{oJdU~Cz6fS`D7z`HgyJhHaU_yfgDL5M;%2TNA{z7kj*-n>__&Yiew-1aK6p#Onr;&Ozum4liZi=M16zoMD9uLO72PSMzth&BU@1gvK85a+L>%YwxM<>+mL%udy#vPdsE*g_a^tJMv(iH!>EhNVdQjb4mq8iMO{wLA{S6sk_*Tys1@WD<ki#-<kjSLe4BYQbqm?7yU3f#wbTZ3ExDe$mt0R)sPB^%@*e7L@*Z*>wT4_ruBL7zSCiLM*O1qf%c-U0a<WV<BFp4LY96_eoJ(Co&LwA37m+i`snp5jRPrRMFL@H#n>v*2O?IaaBD<4as6)suWLN6DWLL5mHGu3z_NPi@fAU!BRPtDIICT~|oIITxPo7SWr6!PL$#K*~ava$}HIfbFdDPkDdE{tnBsrQqg*uKrg&a)vBb(KS984ZV9ZnuY9?iFzhf$r$!^i`ueaQpJeW*_4K4eE~PqHJ~p4yFUPqw96k!{J=R12~-xf9if+=<+U+JoGMY)9=)wj(=G`;#5W{itE&e&q4gbn<v|8a0cYMqWxSATK57Q&*7l$;H&w<YMwF>N@f&@>;&lTt(eXHft@pioBItPu@!2PF2X;$vdfg$UDh9sCDEW<ZaYy@;34&>U#1fawWB#TuCmY%H%R~3AK=1LS9DAB`+gqQ!~lg<P2&mIfI-+okUI{hf=-Cq2v)%ck&3b8`XvEMjl9YB@ZOOL-iuRL-wTllRe2Jsbk3_$wAa`au9hUbvk(>c^WmAJdHe)8b_W<o<lW|=aA=8=aJ`<W2n*Os0fQr4wnDvPiy~t$=U_x^*^-z>rd*h-LL=Tfc69C)g?SCqO<wTXg?r2X`3(Bypx500LA*PZU'

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
