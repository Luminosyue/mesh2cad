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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_003.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_003.stl', 'source_sha256': '511dfc280fe4395170fef4bccd7a6c83b96a57efcc4b59c3b94fc14bd48e8f58', 'input_faces': 320, 'input_vertices': 199, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.056084297597408295, -0.4999997615814209, 0.12916448712348938], [0.11419994384050369, -0.26654142141342163, 0.38450825214385986]]}
GEOMETRY_BASE85 = 'c$}qL3shEB7QU#Ym<9$SYUVXd#TdmmD#_K#RMN1*EHi)NA&L(`1j$EN0YybqKzsmsu@FU>1Vj;0uY#tPnTq)6^|!JzOKml+CT*DJp1r@zoPXBLTC-+Y>#Y6lZ|}3uKJRmX4GV4A%17b99?D~nl`ih%ttg_jQ+$-<=)|O1k<knK&5KWUQ@n^5f40n-6h1NRWj7^RS=>7+dO>7j?-6S6;FzG^0c!7<`H4x15%XruPmGEd{Md*&3!*K4L2N{Pw59hMFnoA`I><jjU8??%e{HQ4OrL{$k6BVn|LLNT&LtZ!hlt!}N4xOqg@cy_uYdaDE}=UPlw2aaa>kVp8h%0Mofk?<gl-Oe^$W5;armU*RYwf-Z4y2gQt5Pzc*ASMPTAj_Gqz6fT8H_>8xOQ;q&%<qUzU02-7Dv1-e?m}yuL1;;_LnsIZor%VruWVxt~$IRu`yUy`b@3@_TqT^MNVkZ#Z`Ckn>S|<4#i?pGfA@IDh@MImDZ%KPjUASL>e=AKUH}`L}H{NI#!I@wF{6<gb)pAYL1iME*+M4bHPusv(cRemegO#UJWn$oV+O#T}>oi*|08$J4x##QfFng>rxOwdKTX30(^1c{G0ReZ_^xJlecc+LSNnW3KDmK=Ho`Azo=*Px%`or%=E2smnIY^JR7|ZjgC<zHDAwbuW+fr@#D?@*KZ~$L*;pdGdH_cgLOJJUeb8|9xk!k$-R{`72ZZo=f>mXrwr5|3`UVdVQZm{&imyuYFcpPwUXQl}+{Cn<$PFF`E3<t$xHSpT9@Ev9g~0^%XbQxvb|Q_dcL}+JBfOkH5_;y^dzOthbWSiFZuuxr+Q-U7+!CJkqJrg>UJ3UgnjAfDCzjl;1n@`i#1<Le57^&NRt?kh(%%pIS*S^F608m&Z-H9Y}H1zA<mg<LpRDr#y}KM=q7ut-1Lc#nCUdOqTO;^i4ZM<Lvh2EO|X>Md`c_15QS{v^#Py`75*I9Tfl7pDB*v`1*a~y$Z(=|6~n~kGg&~ohQmq8#>GLs|_1L>p=<585$z3H}%2Qmu22wZ_Rw_)iBDpcpA^|i=Mn6GmgGM;}J6cGUXe-nA?p{oDm|e6K&Q@)UF;hDVFB{r{8$p4!uL?iPB?mJlQi1UjLqr9OsRg1>|p^tA-ElFa2C&3e7+EqjUOw4K6(PV>AE!cf=cmf+$bp=C>5z99FuB?DK|lzm{~RePM2&p;Mg13d+aWRKRh*&rYNMZVRM1j_1mVS7NuO$$2UX*%yhQKY3+{G+#>FUiCaLJBc@ZODT?ai{oe;@2sMB>(Y1}B7fmLE3T|1|6AS2Uwy)z*12AtnI+GQvuQHLH~+|8PkHuiqI`_$2^8O)_!aTZ=V9B<XQ|zithcD$*vJO*502z~GOiPE+^gkw&$r}u)7&?Z#C>7L_)#2nLl@$;vQ3=-_cc5|kA6VBy7L^xH%EmN?>zY{$H6_K{&3?Xs^4^vc&B=p&(BX6lfQBI@J5RBqA%s+Ec%f9b^0vv%Jq@79+a>N?4KHxO|rHXwd-j5j`Q(~C%*aoTvW^F<cNLD<J@y<T|cC8so77wzGflyOP^Rm^P;Z2OuREIj^aDLzvOoBTq9mxcAfIqj=S;t>GT`%_Wh;i&!GM~Uw=M_><{KpzZAcZIL@~j#A{bWDZZ9)o7R=Fzma%H=q2WZ&y&BS;wte*TqU*Z*!c<byT|7e-&nxw^OHd0Rlm20caEvydGGC{_^Qt);`MY7&ga2uexIB>oa?fF4t+`In^Ui4|Hj2MK3ZHa9v|QH-0tI}c%N=P#r=Az+a`*G^Iy-nMRCj-Q<=BVy<y+byr>Je5wD-{=XccI2FlYBeTewxdo!igC7Ex&H^HlJ=ZUxP7iV@Loww?@sd*G<oI9UmLx*vHUs*=HvuQi=`e1(7DTm95x9>Zp`UP4irr$Z@?R!C)d701ipf+2G$GK;mO{DYO7(JAD!(7Mv%ZuA}+&Z_#W&KZU&G}b8vz7dR_#2;x5j{E2yXnL?zca(48(nz&oeADhGMVq1$LpaFuTSIVfNdoAMDTuz>&Eem1`_XV^)a_w&f{;S1mtu7J|KUk#*_W;>qoq?Y7no_jAOj6PV_9GaY`9Ld8z~4$={eXf_Sy{JM8~RIr(e8NyOXdvvPkqjho}wX9_7!fj7U$ju-QKxO}ltUg!G9*La<8d+Kc-@0C2BUL*P3(617&{P72$&%+ndeX0jPYmmJ!?_YiQue^U#3W-;LtmFMP*Ne}SiDia7o@zlB$KQK_c>7*(%uMF<bNi1Rf8lsO4`Xigd3)f|BH7=#$oGzU?#Ut^KY#L9>znv~Nr)p}`Kp5B<U4u4->G7LUwgiPtE%7U{dSt;|FW6q%eX^v%%U5_n{&I;c<OgAaer@i+ClNop5=V@ujD)@PbA)X<38TkQ?GMAvp!<}g8@8``Kf%)=il2QuYc#c<$Ui?p7aj2v$c@dTVWjccltTv9nX4jK8GE=KGy^m%j-d(Ve<FLd)_;#9?orZ-8b}3Q@)tMJkELbyRmfM8jF-&@;=qex6=KkS9|Z0_qEyTVY*MXpb^B|=brlX8y{1@X2-I>{k`zZ6T~a8rLjNGH``x}Im*2K4j+_7`6xAOcT@ZJJ7MkxdQYl%e<0qzFSMl{s9(;IhEnp!y{X;K;QK56i&8mHZR}`1KgW6QA%EQ0O4M`w4vZbQm;CK_-O=uJj_D1lW%7I}Gu`>U>VND#s%O6^e>+S0tLwe@$@%NP9cjH8C4Kj~>|bpP@85kr%H?^{hUhep+VWw<+wVq)TNi#;e3MWv=c&fNPVpT{(<)rXbNNaBUUr*VA;&kOZc)Fq<fX*h?`<{ZM}GedTvAEx;@xhH&ZYS>9@<?gkEeO<Jn^Q<eDgV9^drCPW`4x}_>OS&yvT8KzN(b-G(Oh&-tWI}zr1cWBb?_w@7R8MU6}(mQhbNQqe{+4KQn`P<CI^OJTJO(o!+sI6FsWrb*OEc%inQ_^eTCL?C*4=WAFia{X2)0@poBe`~jDF@d)JcFS&O>?w6_`<?q>?@dxGcQM>n{aW-B`tCq*#`B@i=qs{rLTJEp&_geCI><K&MvhNPu=J_g1JS6wa{OV`om1*5-<o)6Z&*b$yrB{tSzv`XVe9oW9uW^~j7SXgmwSw(6a=Xg+w`n|`HxJdw^Q+AHoxh{&y=&$DXioVnuQ$KkT9^E@y=mS}$EI4B`E4lRc2`%{%KKC;>ca2g@a{+CIL7g}$zL53d_*1xqjJ}okT92D*$Nx}lC67MA+6$}_$V<E(obxH6o0n-_dl`C8vI}V#5QPP;Q#v*+kPvDx2;lU6@hm^e;3>q$hU!ojFa#i(1q+T;UUob1FMkTfJXrj0qy~PEbu7czR(4Zf-dAR;9S@?07pUJ39cA87y1FKRDrL8tr$74LO!d|{t)zW2kbjwvwb(fZv)yK1)pNri(wPEw^f3y(j9n=qz781D{v6>hr#^`G7wnE7bQFwx{%ot-U>Y%*nlhn-VVGK_|MRbfVTrzLKpZQ=t7nQZ-i|f@H^0705=ABBXrUCf#3(iCh#)kG8cF|^dNA7z{{YogU>SHBItIkAmDY-$5~~QRYD;*13v;=PsmW<cCfXF><KKSr-UDc?g{J%`8cp2unO59cq;JYz;V!XfTsd)fiCba=t8~=oM)BYu<wQ~2mRX%`(D`c(Dzc<OJUoLoF^flNofCZ^f46nP}pqWJox3I&8hI&4Etu-1U_MvlUAvRJOx|>+hNFh;8NK3LLLU*3%nch5b$o`U62QXcLBc(Sq5ASd=Pj)^rOJFzz3iUTn$~wD&RV+9D)4^Y)8>Q6Lu4}I`sV*?8jg`g`AHgpW|r%Ao^Gjdp&HnZyo&V&}J=sPQiW(Hh~>hDYQxfa3u77;3^;sfsesvLRJ7*pf5Il5Bd?{YREmn)xcGdJAt<W?*Yz*J_mRka1?Zb`#~3S7;vmr0$>k-Z4Ub954%5XvFLjr*!#d1iJbG1Pd?h;gFY6*UI?4*8w<Z!w7CsFk+4U?Ch&b$X{Cq<0ZVt_2VwJu^Z@Pyn?IyCus?7Bqz`Zaa6ib0fcpUtgX|0J1^f_j59kj7djWTYF0dbTAyr`UZ*-opd&2er`qv)z_OP`@-`m074mNk>d_VHJAMHPcK6=3J0h{gH7JhBfrWbtNVRwg3-~_7-vPul(W56-MBOyCWxHWVkTL6o?9bxYXo4~$S8Elm{kiCH00JntfBH@|Pg$xE3brWGvgsm6yUxD_8905ECxFci-2@i%o82NQT-9*?EVH<%ykH&ZinJ$e_I@(W1eH+h&J`=H4pl&ei!LX%c{M;~xLUsb~3_KEYw1m4r?}AvPQMV=REn(|~K6k);2&n+K25tfACgC>F+aQ)3>iWX&3!C^$waP12NdbNhx{%`~JP~>{@N2-6p)UrP3LFi6y;U--k_DUzJrix(I2HO@;7s7f(BA^L9(XPEWUHiEB?)*X^fcfs$n_Fl4Sh9Y3A_llWZ>1%Mc<~N?*dPQJ`HW!I2rouz|(*iL7xn6BJk_b7g%MXRi;C}1Uw!1Iml-u{0j6}kk>P)n*w_ZYyvO0${MRIh17wU0xy7EDB%p~8HlwIb+cg4f=%H0R*ARD6391!mjEw^TqEH$=xK<x26dBQPlD}D^jY-pRmkUoUj?2I886`}(5E0)JnD{zeLQReM_6T+Ri1?m1AZ1b1X7dm%g}{<5?Iuo2m3tO1b)gYPg^A%at3fXa0KKm3D1T;8?k1g?gZE;z$Wkjs|>ZuaL6Zs!$RF!__X{_|3&7Xf4VpvT>it%zt(j9?3ZiCSh1Ra1PBXt7x%n%2(_Stw1;?MEB^q~q4);'

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
