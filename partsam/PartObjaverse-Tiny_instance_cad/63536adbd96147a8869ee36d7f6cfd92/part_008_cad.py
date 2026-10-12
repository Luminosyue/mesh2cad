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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63536adbd96147a8869ee36d7f6cfd92/part_008.stl', 'relative_path': '63536adbd96147a8869ee36d7f6cfd92/part_008.stl', 'source_sha256': '7b00780372ca43d1240e8c49bca39e79844f4c1485179bcb2a8a227bde7ee9b6', 'input_faces': 205, 'input_vertices': 173, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1355017125606537, -0.49994543194770813, -0.22276607155799866], [0.28187060356140137, 0.03411105275154114, 0.19739758968353271]]}
GEOMETRY_BASE85 = 'c$}q~2~-vL6~;#t4QeB<QHeSlQA}LG1<`036g5#XV#I(;eSm<93qEiK$q1sTK{i1I(TAWSh;d6qR2&y@4Q^<viSm+~xYQV$XtXAVa=&}iXis}iPfN~szTbS@cjwOkKkvN>jvZCEUJHePIw~RaZJ!j|D+;Nx(n47fWR92-7!=-fPT1l)iam1r`OQ<u_;`)=tD`JXBD+ot3J)}Q9jJC46ztZuyV^B)t~tW&KWFM(^Ryt!hx^Y8530?>r~8Km)gC*!^zYMM?bEHhx>Wrie;U?~V6^u=cC^+l*-fg*)%d#y$PIloa>e8EEgVm7eGtc;M{vD!CFi%|KOxuJxO2Vv26Ai2@Dlvqvk`J@u^0O5r77sIMcN@(ZQCI?^)EV%`kp@<JWprj%5Crc$Y<U~u2)#lUv=!g55M=>h1{qxquz**$9c7&t;iME6R5W=u-l8*f1QEc`e+(oZx4r~c-_<h?w|b)>h;hscH{MTr*M5#N1oHJ=^oT)y@y=2e-F9kX*Zr@e0}!p0erm&&hZ>&U*SAT{C2*sFP<F1oYh4~xqmUw`PY~tyl%D^&-LhMzTV7zJ8`^pV=0cSqS411_6ycgTNI1j)Nn28wY*^ksITmc+&IyS=e+U#4)i~H59ha}?Bji0bTuEZQ;LvVYp(M8^orv7XZs*m6Rz|6R88NG*Lg3;zNw>2P_IpDc7p5ukXtI+^S<org?gpYokOVqp08Igy^)94g?J)Y?q~7(OvphW!*Lexr~MP|GqS^R{667l+>ct!c3!txhqfROd4$}Ouk$?GfRlWmE<tX+H-h^t{08UMi@qyHoqCh!Iejt*zyGZ20N>}$xzD^WE%1I0eE;Td<2n7k%J@9qpW?b4YIvRh9E<sNlRI*~;e6h&qC2@b9=Y-pzMt**KG{>X34SUD_qC;^+$Yb1%8}<>!ToD$S%W#1^pb48-`XKpMsMXl_X@cG%sAYqR_73&r{)**(dGvtS2OzYb-lY2eU!dcxZl;KXLx=3eSqsy_E&z)@9WuI|Hf9XKe>?e(Or2?k7cLep*6hE@jRzy4mgc@Je6%Yb`9lu+Fs`C>eDip_p#<Cj-UCR!Rs#-V7(QGkNJ92pQ4X)eAH&1e+=(er4!fpIkpjV7w<qHrB$7?@OJIi^PHtzzwbWJnUb{<$0=h_Z{#*Thuk<2jJ)Ot<d)J|-2c|&NOxM#VsG>@<+kB`)d8JywbYZ(Tb<2))-7I%JR^|n@9)JtdfwwC%9YA4JdaBk)a!$rB~xztp5MR5qjJotXEskky=^Y9j}prLpI=Qy{o7uA-YE~cPuh?)<S{AS=NYeqo}QA9`J3EFy>=r3_1gX59LhECYVMQQ|2*nrBXe=yDqr5mO`TA0boAclj&**{_4ResD{i*=IB)(bp7X*o&LfN+$Q!2cc{ju&H)gmNP_E}YbN~IjdH$)7ijY_2ai9G$sJHC3*^N2XMqEGcFwcMDG3WbAxPGlS&!3&L_r>edl{D0w>>usNzPwe*`<~H<*R#WfqqyGXl^>yg@!r!oF060BA00~I{d;nXjxC$Jab8`7dadUZ)N7L>IB$G23H41JP;ace!nx^H^ikgTJcB+5)nmv9bzg(}a}Q9jZ*bw<2#G=8$ScUT{{1+ArYGaP9WIn(Uqf9v@9u$m!y|&vd)$Zfh|iYc^^4L`uazz5JTH1R)}hgL%x^e<D*4J~$giD2AM4^XoJZY^#rz}uP;YX)&iUHym`8W2$MvesapdRc;ChX1n~|%l>v5jv7Kc9LK1OcZ=ft^l8Qy0`eg$&Hw>RgOZK>$<U_RzIy+4U_t-u@C^TSuXFMVdc)JGfoD%X1~;@meT2J6;t7tiUln)Bhq($L>IuMB+x(>YJ-9)Lcb8smEP%yQ0Ew;8A(ewnXp_%%82rBJx?kmvD#$oZxy+z(2pINq1D)tp~^9*uRoeU<mU*Xt*cZ`r>N`LCCFo_XCk&lnVe*XMX}z5558-z_mC|NKj?PYmPSaun;VO}fo<IwW(hMGS!tDCap{cSwB?oL5PH%6(duaPBrZ9M}78J>K`MO3ppkVc(71dwd@bzs-4zVBF7|!-w3zu*peYH~&ERo;j#DLR~noP7lC&3m5SEboS!h%_biG^GERfArm<_#rR--G8%LJxj4>GA6Sg@_6XqnDlCz6qw`4Am*nESx{-hK#rx2>(wyI4-#q4g@|0DW=bc%ow<Ot?@xHpxMV{G%`}DNqeD{{6=rc48xiZv&^YcfzPxu}jYmc2dZ#`}a>fcSkvDMj)bKfMqzl`h4%lLg<_bk^p#`A$G?&%?%w_^*=x75Y@TPhkI#<7hf=NEm<$n}oMjp7W>%l6>=R(*37a_dhOoICC0@3DgO+~<!2&+$6vuElv5CzhhV)iBN-4&r%HZQbJt`Zt=+`8ahQ*6YV$&Mzl&-a3cBw;NQUj}pC^^T|ij(LXu@pTFAGQqHwQQJCL83%T+2S()dxVC-vkXRaST{yg$}5qNG>1~<d!tkK?&^K~-|DYq^gjPvTNS99L`a2Dnq9FJU^oXGj2*-LR8?8=|l7s@$*zF;f*Piuf&n_&ML^0w~yJ~v$YA-BA<hVyIYT{v&pbe_LBmGk~8zHhBIiO5Zrg`C%S<o;(4@_E&VoE!0L;eY=NpEt#^0>^^};(N#Vd?G$awChQn*R;XD80mL-9nO5ox#tzkV<b*Qu7_AT-<6I1GF;p8=lJBh7vNc=__<*DQa*3{@tjAO@SJgLP;WHI<b1pn=G5=;_lI$@%SGf~ui!b+n9>BfzS)WMIt#hKxg&Bd%9Zn#3-Fw1Y`KhF9proQ#dX#j{L1yWr*W<}$8*0?JrwJpo{Qw%8t@^!c>r?jt%IBoamN2gY5j9}&K2dHPk1dG{i_di|K8U)e=r8$3wrpc+<%^x^Y|a<V;z<qN3QR@!+Avl?sM%*ET8xBGtPH=hoSCa7Ju$nxLo4*sVBaF^%ED68;8bl?)h*%>Q{OoHziNteD)ITul~s(&b#d7yj~2iLv$+lN!i1>F=Q3|m<74T*Y+}wJ7@88@weZ-oL?-*_njX5H=gsYhMepA3iN;Q<8k+~Fa6cy@Q78JuQyZ_lAY2*3HE>CPaYJ~&u{+k|Ku^F?|=0tkKWGx{@*`&IMvS3oi1PeO=0q`!sL#^j<`hT&cYo;#BIb?Ve)pu<ZXq?UlVR4+(Ja$RJ^4yd2?ZMdtvfM!cB!6i-_xs+X<655GJ<~wvp|tFTyP(qMuj9>j;zA6(+Y8CT}SGif|JVaVzmZ2$R1mOx{eGytQyE;nzjPZ-_exleZTp?<7p#MfeTjw?xFf#JdTT_YfxUDNODn+)KExh}c!Uw=lW0FnJ$g@_xePZo=e)g~<mAle-I(4-_UJAnYpKUqt-2i1?2pVh{0w!ULtRhqxw8K1A3<c$kQIg!oWla!+CM;lkwa2#*kcSA3*!a;;Kol^`NsBO+cYB3>aPUM3=r6A>>L5yy*&KN1lqiHK80#Op=GSt8<W5pk}FI7dXhRYbf+M4Trg-XtR4C?d`f5vPeK3#SPuiYEvs3a=Is$BM5JUL$K4D<alK#L?m_gjdL#MvI7-iio4c<Amd6t)oQ5ABu=$#N&nIWe;LR#H&QaYsHg<lVoq!iip>Vh&PC@7hW%Wwn0R^Swy^DJX<(h_Hw(3IA26uAf6+fBYRvRBHk$?E)?G)Or9rPD7-^NyiI(QF!@H|ZNe52ai(~NFnOAArf|A=qOiGEVYON$A`TZ3&k_;O6cLArn}y#OA1@;QlZbe_h<L7uI6~YkY?e79M8pe4#7jiPks{*7BH{%i;`!p?!r^i~^F_q-M8tE%X9$x|6P_bHTSOcxA`TW2n?%HuMZ~`1e!}Eqg?)v`iHOIDh)0WvM~R5NM8xljh<!xFABc!2h=?bO`w9EWd=o{)Q$@r<;xmM2$a)2dhyz5#Q$)o6BH}>tnZo2D!hyn*M8w|8@Anz;*im(CTGahd|D5*wk4_IGFa6`%zrOP2N75Hx`BQDLe?Fj&9c7DWADi0$=w|VvrwZjCaXD<0'

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
