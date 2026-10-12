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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d1a5633cfa0740d59bce4d3ea051329d/part_005.stl', 'relative_path': 'd1a5633cfa0740d59bce4d3ea051329d/part_005.stl', 'source_sha256': '397edbb12d5e7750f225c2c619e16b34694de1b14d9cbe76d357bc8b04960a32', 'input_faces': 248, 'input_vertices': 227, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4950654208660126, -0.3562541902065277, -0.49890100955963135], [0.4950461685657501, 0.3929367661476135, 0.4992675185203552]]}
GEOMETRY_BASE85 = 'c$}r032+rf8pkI<a5)x{V?hi$7-9s1U<inSWOPB)fC+NMh`@W~fN+xtB7zPmu%dX76^N_hfuIZF(%b^c5OQHiNRYfh&IfC4m5Q*iTPkYec7Oe!$4uvK)z)sRzWV>(|NCA~_e@W}o`I-{_8odD;%|VmR!#3z)>~0{bX9sOtKyShNQ{k7eqibHm;99O<nupMQ=XnNB`U^GS*5%j92cJ)n-n}o4IY;;IygiPPFR-oLXvao++|5|@!Wshxi~qV`N<2M%j4PS`$Iz?3Q<Q43Q^ao|Kne0)&<XfN16+mszoEJNF9fB3w-#V1^Id57T<85Eb&!u`f|O#;@ezb^``Hw4_Yexg=2EKDs$I}yyUy)Z=rg%uYUs__f#PDQ!l+(ZS^(h?h;?VzWhM0)mQpt*3<EJ9z4v|F>OOufe&AOep@!LclB(jvz{Nlq^i2W;+y9|_RaB{zR_b}opoGBaXR@*k9ERNyqYb>=c%IpcU)I%?T@jh|Jec`zT?$T&(gSlUU{BAH<i1oeqqmYs{6-{YHR<EZ}RG_zS)1-H~Vk;o@?KU{uT`t?R<O1<{Qqu5?{W);&QIl*RNHG`r<TdNBL%h&G*g+_}aA+)bB+9vuwV;Ff_;NtCg{Io{Wl}=P2J0Q)~6j^Je;<idn)>i91B?HcYD(-;X9=uXvBz(Hghfd}YVp!&cu_5h?s_)2SV$akIEirw3G$hE3kfuaj|M0bL(YS#RMFoBT2N^@|^o?<$U{pmr+_aa{N58tO-Jc!d~89{Eab3;9~{FyWv5iF~6blYFH(h<xSjb>X|eAz#g(PxHdlm`=yjtLD(W@tl}VzR|cx_|+-!qsy)HO0SwmzHwqI`FeQuN#1|0>S^*_C#I0EHJze*t$H)+C!xNa>Xqu(gn!V#RLqn3N;(gx`iT4JV2ik~R?H$_E1Dwaamq&qwOd~E756=k)H3SlwjJ;*$#>1`beg{3Z*0DpCxdC8=s)jnqWqmb^ToK%h;c<fLdSFT$~bPj@2&*Z^Lj_e@I2djXqZdaSNHFeXB%(hcJdv5?Zy3H`!_coZ_H2c`tlvKN53C#@r~N+KI=_iuGc(47k$;6zPJA8G1+2%hS2=fTjHB(KHlss{CSIai~G<m#(T4!SdW~i#C_e8N$axXrxLMVMvgj4^{t0RJ2#%ow2sRYJMch(4_{k3;h?qN9G6^g`f|NFF1g<H&3e!Gp&8cer8NI0)`6>oGpyIkXdZEa=FitZ(0H`cR$6DY*1tDfeLdmsY^(43tT^2|e~h>tG~d)CBhziyck;OmU%ooya%Q;2_g-JA-t^^q@AZ}HP2a3{92tt^)>Aur)EDCX?&!bIHvi{O`jY(Dm$+=#%XuRw+~Rw$i{yLHKYV3lyvurAHKtXZKjq~#+xeOKl+E{^2g&!27ry>gzZ7fx%G`Omb|3fMtTj14{n#zJ;TGR}-%0geU#j=scT&CAN4=-0cS^XAe%|u!{cPh)?a2LX<4g5&Kil}I*M8i%%X(bL%usRu;orJ0cK_CO5x%E&q02g6Bc@%B)%UjJyh`)L^u6uCcij=VFWkrc)CUbox3+K2XLZnsbX)(;`vQKO`%Ch@_ZR#&_m|{*>xZPLTl?vWOQm(dv-{>z>Q6#Hv5vMJ6Z_gdE#zyZO10Hj(}!k|FRx1nMrMfi?dzE5NKB@6yykjn`trIe``&dDzPzr=zFF_eI+;bsjT}$wqVd~5Y5mu;TgW$mFZ9;$#kjIN(LP%KebI9s7XEu-;`a!@BaVE(T-$s$f7c}6`@06e&F`S(oApZJ&0Onw)*DmBzOFDR&w8HqhIwLNSAFp~eb3xCUKv3BH{5sR+vX?s4<7db^7R!>;&=Pk2gUEBJBWO>XjGNe*J~5WR~C(@`$YTY675g4>)Q=dc|UXgL-_XnkNRVWLUI1_Jn~CDwWD-eUt;a2n!M!%X_uA~(NFvSO6%fZDt!BXObM7&PM@Xyn-(yo+<HFE{hk^y74`Q0p%xHbZadG|PdWl-lP~W-^?>>0%llPFU{D41L)zaOfe(@|?}t5sj|yMjKM#x`U*2!4!M$nx^8Q>89w2;qKR+Z=Jcmj9e=Q`MeEB)T^yTLWHDs3XrRNb>NG$pCbB*cC&o#1dG^N#2KT=m$iT=B39a0+n$akc!C0`F~66;fgKlw&lDLpsK&tIl5KY!_I6{we<@8HYNcWwOdO6#a!yS@|8>(cY4>C4ZXrY}ElI(FR<?*pXgU)fi#w9;`+Uw$r@eYswKUY31ty=&q*8rP;Uv48#gF0t<JIZM7?+C|)N*G`LdX75zG&$W`{;{C(**$w=&>r>@C)t5aZen+ldp?YQiBJ!2e8)6@OeFoL*`&XW~-goBv0WE7)t#!V6UfD(S#*wwQ);53e{z3M=?;nnRe}VL^E41HKzFb1%QIA~}{=1n6ssF_j>AX0O{Y&^8C(wD&PsdWdcI*e?Z&@q$t;LbzIu-7#v(6Lq{fX==W!J=cFFa9ayY4khYlL4Y=2udWJmDvjZxlAz>b>u6B;P3Ob<SEZzyFc_w)Ht;{<t^Uj@#yak>s20cnTZQpD=NK-CNPlC5)?^cpi1XA;x>^SKDz7_a`;tz8X&RMJpO9#_Rrod`HnpF^`fu=L!FP(SA`>y{-SXpVf$YnOSd}4|ty@`{w&JwPs1P?Rw$8pX__z`?<xwKz?s2`{sK^)0f{{%D!ALzqgcqs*ke01&$rv^Rn8Nm9prh^imR>mRG>s<bS66eg&Ku_TRk%4jcXdz5-s(`jE(CK7z9YIuGmsM?;?lM}woF&w!)A6QPs96TxE<oF8Ek4t)|j3H&5@I`kRvbZ`vxS#S(E4muAU2VMkC1TO-wfG!8G0I!Cw0<Q*dfa>54;4RQUfwzF)fNloA0bUP%6}%q&B6KDAMetJS67W*+Lg)hULU1h9362HNhCUCT4W0&_3Z4dj0{S@k3GjI6IPiFIIAR>G=UC_%=s55g@C4}N;0fSJ=u~hdcoy_|@GS6Ls1rOFoB&+_P5>{4E&(qFzW`kc=K2cwWfqfJybgT~yaqZ2`WSdWi%(d53f&7n%HlBchmqr)$08H?OyoG{u*g6@13AuFEIvp6bL2Q5VQ~ogL&$OdD~o-|??aCBZWb=&UC43X#Uc&)G~_sc#NtEbKSYl6Us$9fpNbr3zB~?PF$%%?X%+^H_whZhZ(G{n`X++&ThO<`Tweme30;feybk&jm}?SvEi?kb`6*};nCnb%1oUA9=h4ua;F%cHXy{Nd*J0pc_&(<l<c5HU;qzd4gTNv9d_TNk@L+tthsC|{??sODT`c+|-yb>7{9hmYBHtG|&VOKWC-Qe9$GH!Se#rMjj&lHuyOF;eInFAJK;#3F<2-=HK;#D^$2o|_eaPR39OnmE3`c%Aa-1Jz5sG{$a-2u72tz&$InI3Dn1TEZ<T&$n<2mG?Lyj|FH|8Ke2RY7s-H1m%9y!i@-B^bFGUPb(^&%PhWaK!fu-JzDHsm;OM{Wmr8$R!Z_W^i2K7Y(&5BxpIapvpGUgY;8$N5VZU$LlSah^pviyCMZxC%8jP&c?1-?;#-0oS00b2^J-EDo|LW^sx|DT4D!7AII7XHfvn2bZuYLTwSg&-nn0tt>u+z6bt-#XBr=p??PFg0rFTf*)n^kiy>^3mpmG$YK-P-h}qIqTbAF$Z=K`F_(L=xPwJc7PmpWf^P$NgmwXU1b2t_0QW$f-Ep2yv#5hMfa|~)q4nU4;6i8_xDdP_dKAp>=WdF)fBQghhjs(s4(<SL2krp&hqed%gF7QQcVh87s2{XF*bl5g+bOsHIR75n4cra==6r@lC5uLAGq@4l1oeQMz!eD2XIY$sUWR(Wm%*2y&EQMmYG@_68k~pVoC7@r=9&fObC=JtFQD&$`TWvYyaxRvI4Z)gU9a~4>A#rV`qTMIwf%<^`J48~66-fRvWxG1NQsK@?<g)rJK6|4`LBlZZ=2Ott^'

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
