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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_010.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_010.stl', 'source_sha256': '863e843f3f2ebbc3e97a8cedc7ee05515bd3e292d98105e0898a4fbb8f9f0a70', 'input_faces': 254, 'input_vertices': 175, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.029899993911385536, -0.4999999403953552, -0.4425329864025116], [0.3382088840007782, -0.15427911281585693, -0.10594172030687332]]}
GEOMETRY_BASE85 = 'c$}q~2~-qE8pm6}#3+e~Cc25i@jz7Y7O#l3q6Q@jf~W+K0Riy<6$At&HkTOjzVIMA29X%Wc&>>TjZtnK4iQaM<|Ss=UCrinv$@mt)xSygzU+JZcIUnC{eSbPrs}J&tEzj306%+&P7;50mtqR-ydFA95(`JElav@4w{p>f$oK)V%adD4PUN$ft~;g$PYnoZB_&F$-6A667sR=ZHo1+78tLX?a*J9Pw=ym)cK))sh)Cv73R@Z<srm8IVap@6_k9MB@boYZ?dxGmHT{pTwpt377Y`gL)>Q7<v5~3ma`rW*s$=**rqY8Bx0sqk`dt@&OL(W72LFEFt)wSXc>9_YrJ`@kJ=P%lQi($*>5q@=Y5WCkxqrSiNgUVK-m_fv^>JJLpF%>#{7v^7xu2Vr=*`A^Z!?W+vCbi13GT7pTWmjbMg{pl?mo_Z_2_jP*W}x}mi+HMiwyp#zmTuyOni^}A9T5i{JLRvqA&Nn(J1;#{}0Gl`^&c}-`LbzgYW9sDEemA<uvmx9=)i&y6)>b(U;s7Hj2K<>-ZV+=iQ_B=EVmMzWSu-rszwv51bYAH;*}4FZz1^y05PPl6<v8IloR`{YyxD962Y}$9(e_-agItXXYzo8Yv&sjN80Eu@A|Y=k%nyt6PJvP#u=VoTv7UC6uR9VaM0Sq*dp|x|yR&j6Uk7`_k7{?^7L~?4^0BYcnV>*`vYWTaNmZ%0D}PAm(q`IEvPbl;=UdJp2Of2dQd*G3Dhv-~#38(aiI?a;{1ArGnsF27g=X1#w(+$t8ZB&mQ9blxcUU|60c;(KlH>YZQGcz1Ky`Q+d9O`W>8mk?*6em&mW(K>e87hTIZ;i}Y@z=*w@fzD(nmMe_C&i*Ad)($?B2`pRslVp=En?LVUT<3bF+>6<}~qOacVM!r(NvYP6tOs=GSc70C18X9G#_Mdd4zuS6uR;kXFgXz88eG|>kRydY?)8nToPr3OVtqb|otK_S<?oxZ{QDYVLR~fDvuFHe`JEGrmUEr%OS=`V1hOf7nW>VA8tK?gX*3mwc%6C!zwgol3{U@`i4pL!#ljzHB?%ouAb=OzCy}donN3M6IJk@s2C5H9z{WH{``A8D^YW)@3U*-lsevV~rEfM#TdFG}Y)L-p!-hO5b^{={Hcs<`JE)mz2rRwk<(bw0N?wh<y$v0md%;)=1BDMW^t3=$7YMhP6l`4|1k{{#nG4-=Ng72sMIpoXJ`TfA$cU=wjGymPI;(TTMfiz!r@gwqW$6NFFU5+-1zS{Xpljz%myM9R5Wu7}fzuM)~I+7O#ekiVg)#tT4qOY%i-8Uy&$(M(8rumqE-bMY%PA=Cd&n3kl()-iVd_7JNC12jzhhLY2XZg8ZGxwS}FJ<FHK5na><eS36sXnGtY5YDm%EtTo?hc)M(vxOB?u1#_$+vf=^<j%pNKJc6xL*)rHMAcQR7&$rh^6|PzFfomdpxgH+%J-UPdX26LspS5*R-MQV)@|$zrNuGrH1u?Z7Q`_+MF&G>u(DEJ6|VTT+7HWY@+dO2{P}0Y6AIE9|!Wy&vvK%qNG1vPUEiG%h$=O5PqFE`Id{<-IREj>%rH{4f|qqFMgfJt>FFaGgDnGdtRn}VKZMS7wfD9UE}vR$7b@Circ(Co7>X$v`rjaA<oNk#Fwv!)=?GW`Y|=Bb)w&Le!{nS$B=I>OuI|(>mE`5vipQe%D;Lh&+mLSjjIgJCSUfyNbAk=WH)~<D$lDlte^S$eE)eJBVVm}={}7cIE&^dx4v5`)>E3~&Bx7juM+c77CqsAubogO?o%c04Bgk1sH7^f{^r0uey$(QCSN}{)b~8<L|;EQbYE4rldt~zYcu5$6i?%*E8aKuKmNN0(bwzW;<tIk$JNi(m7@)Q%ee|)34F}^vHJ1#Hav{ZKdD{MYOxNcAt(8~x_VZNbvC7!@jAB-tQPBRO9-UTsdFEYuir<c-2Qc<uir;>Uyk`3_s@p#=iu0f{Jj6vp+>Bar26ygGpl2bIIjA*2fscA5jA3cq{%s4f4V}xe*cxbC)bO<e*e{dW&aO`acw8k`Ffb*bi+`esz$!9ykc*N>tA&`dsFmV&QJKNYYzGP^MmDO*Lu;{pC4NMvR`f(>YU|E<4citR&hPc57T(PxB8GTy^v4)#CGZlox{rMAnPC1Q_WAd8un300MGZHVm0jd%#r;0r}QnWxIQi4-sjIhKIg24eLa2<e}0(uPpe^HY`@+h`YrnczWk5&wc@<gCEwDxYWps=hIMuMr3TS&Sy%9-6C-NHx=AS)_<415S*>9`e~`|<-{dYg_|m7-_<8t|QY+R?N%G?7a7kLNIA67ye-E&n%BdCWqaN(X>l$Y@<}-RJ&BG?w8Tzq&9L(!_{FY%{Dfv@A@2LKDqHkH>_G5#O{^gD~zTO|0>kN4&mGN=!Z87wtepbxyzh4|O^kbV4&FfZONxn3)hVG}PUtQ?=*__h7o~~B{zyC>z`&9Z|*&6OUPoevnB{2UI{XOY(?yD8lk7{>_e0lAl1{&A(3O_eJ3aKA8XBzo(@2~6m^(v%uLT*ane%40*Txcu5O#LsilCS*m8b3$OF;{8)!<}zZ`!i#Bp5r&r_YyfFg?wq8Oy{9#|8vw{RS)s@16K0;=$>o*yiECtd}YpVx=)$&Q~39Z@m(9KpKUMH@w%Pi<6jEm{)kBaJhwNC-`@v>ldpz)@%o(nisoe-UclS`^$TjRhWeHl2N-@Od2{6Xe?>b=5{qY~PEu5u@Dm9$*-O_y{)uGKu>a~Ok|CbM{@<TS*l#3HODs{Y4q&FO1-}hErcZ&H+Jl+40=Ggb9H4gK3@x^5u?fL=2Xs4_=@#$~@J47lcq4cXG!eW8yac)uyaXJHV7wHX1YQbGg=T;=kZUS}aT<d0dgu=D4&=8U!B~N=0W09;&?VsIU^6rlYzBuS7>7ZZg2TWopsC<g<hlZN&OnW~gSQ|uP|I|1A|eBI%0OKh57WY3i~b14y`eq9y}>TfZeXT8z%F1{Xg{zk*aJEg>;WDN9St4}o`7KN4IKs^hFrZ7j7K6E_l5Qb_XYQYx`17fUoQmXK2Q&EAMgn1Snvq2FLVOf7d#cgcrw%*?2TL}V=kjn@6o7*JG39TA8P6j?FR0K>%n-N7CBm^AQ;DMu@IUC%>i$Q?t<okcY$-E+rYWty$HrTp()^<;5QJAV-Sp^pz+`+aJZ0bID&BqKAVjGm}U$8XJgF0(6<nb_d&D4nOdyXVn2fM9t7hJ2*!)GcpVxIT?>u|CqOg73E*TzCdSUhc-e^k$Y&o|&zbQ7=pOI^a2|96I1jvAi#MUGp&P)f!SkVu!TQ|hBN)%rVv!beCB7~;gR>BGaXpw$11|)JK*xibP6Q|8`XxZ4gjz+RmQlFg(a;c~&LPMz1bx1an24O2P6EG$dg<$vaV|7Z`h5*E*4KF+=9-7vZAKlK#zJ?4mqFiz>a`EjVvH7pp??Ao275wZ0(*jkq2s{8;2`K2u(KA=Y0(M6*a_+gb^^D9J_~LKZV&AMZV&DVeIDEq+!fjd+!btsz5q6XUxqq^osp~VcY)Uh{W?QCfIA>RXQ(6C5%XmHq86RC2t+UrfOZE5fM-M9z_Y<~5N_zh4gE5X(;`BP1<-k57O&v%Oh<v4dV%A>5zrxErUQijm=1yt03X)ks1}6?#>b$?!N<TS5R8kU?}C{g0T+SaL7({;=P=lUV0;kzHkfGv_#pTY^d0a!=>HIE;)i;S0{dWYY>vaB1HnvX@Nn>}2*%T)Q@~99!PCLBps#^vfoDK{z&^-l2I^KM)U!yac@b)m4}Kd_gn1WX&IOpu5X@r=a`lG}1P??Tf2fy`uRrqghwp>%LjBl!TZOv50``Nh0|)rEvg>63pZ=Bm`%9sRckv&)|Ncqi*BkMZy|qo*@?|H$uQmIApgsKC(Zgp2+u71@OV%`8'

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
