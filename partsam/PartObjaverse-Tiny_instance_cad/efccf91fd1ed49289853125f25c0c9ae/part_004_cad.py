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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/efccf91fd1ed49289853125f25c0c9ae/part_004.stl', 'relative_path': 'efccf91fd1ed49289853125f25c0c9ae/part_004.stl', 'source_sha256': '39362bc481ac46a8ec8556cc986840538fa5346f223c2e48dce0b5b31d2a8127', 'input_faces': 485, 'input_vertices': 308, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0505923368036747, -0.049979984760284424, -0.08444725722074509], [0.050610098987817764, 0.22768576443195343, 0.4999998211860657]]}
GEOMETRY_BASE85 = 'c$}r12b2^=8pnIdIW8ceGQ<T5B1uGWM-U7kq6nM<x(JKpu#0ejaAQJ|v?w_)2m*?d7m%>CAj>WpL6QP1666p`rve_wRrUO;o&Bcny?b~2-uM2$`FHhKUsYGn(AAH2t#jszc0zv@o%T1*E{VI(adZ@NqMf1f2}62!k58;KV9@X=r<m*OKcgSF?eJ{7m!h1Z&d8V^@rm6NVw(73n)YlQQ_C0Ab6~=dgl+>~9hlG~Ui+=O^-GLbeqyg~gW}ca>h<e3uH~y=qn2-!?|=L&pi1yHyRa-(X`ss9O|eR|I?P*_YVn;>6H{X?eq7s4+rxc--OR1FJjR!KjPL8XZimhH54^G4<_C}Zj#%4Y9DKs&2X5p#X>EV^?&)yfnL8(F>(}_QU$4FB*Z8tuuf6CuZr=5vZQhJ8=gs(X-hvAbr`hT^zO3K#&&@e*^JV>Beo=p5(c9as>jyt#{ou>`vzBFr*3%O;)2zN|?|gP<yY)JLdG>2}eLhuxo6V2Nv$D?)>$q0uNe^A$f!VHa^6Fx)ANNY?PMa_1+4IFbXKgu~VO=MwjWccSlY`?kL;Ys%wE3prxW+4%y7g}>wkzBZHhRwWgK1~7<@Yzdvc$b^X(^fE^*Hq^xW3b1oqPR)7n4rdeCNiw@3Z-=bLq#;-5j*#iCd78W@{f@7`-jDo(u1>`DR?wcg}x$JX`)%>F)In{?t8NzkyZXxPEe6rwp4f^LxIzE-|kza_4P-*=6p$^*Aur=KETo+-7b6a%y_GAGo<;rR#Ujm}c{xE=|_k{J4ItHf76S{MQs)9^?B5thTlfj@p_U?q^l4vDr2*<Hrr^xY^qN$->#j8(2QZz3&1e4@|WAGLP4uJWj=<3*B{fds=9{_j~tqn{Vbh!tc>6Gu#i3nlROt$M`aj=aVN;VOS`C`nVBpyF*6~+x+0A>feR?!Be-E+u9pHc(zAqU6t>&z^!jzmA&EXFv9;K>6p#;U%KwD^Q<zHlHK{d-E@`PuKTeWHs7qP2)}QhP2s-3=-?Dv9^;#J72%KA8v5NX9qanR1$#pG`x9;4x~1=n&o|TNCwF;zr!`M}_e`4~I6me`xbI83nr_Q)e3{?3C75BWGdUw^x2<2}n|`xm?w{|@=lEuBfBtU0Gi<(-{>i~`-$|+cLae2|@xAsXPPym%%8%OU-bbAa@3i^B9$hnSe%8p^`)z*UM%k0$epa>N?){nEVfGH2@9%qem(33h%fHX&JHIW>mft_SNzj(x_;Osvm*X<NtjGAW9^=b-@Y;)cFutkZpMSt~cU<T9x!+sCK~t7n{a1cjZ}S7~qjrS*!Tu8_yMEVR(`~-Y@A)FXmq+Ax+W$Du9Z&l<i&HIrpt--Bt-b8m^F_a29yzX>Uu?1UYkb+S@gv4-d^ukH<iv8W`tS6g;*S5HU%TI9{^29{+5F&<AHNOvlk-kp>t5er`2#jTa447C-gkZOWZQiweX~BLZ`Pai&3ZGwyziuM*17b}I+wm#x5k(Eo%H3n<b5Z7S&zK$q%Y?|-gnYB^~YWApX9DLe&5aar1Z`Aq;F&A4{Yl}`er>CU#<t~d+Q;8{0FhN{KEJ0<45EdzR4dqH6bb1HeTU-<DIo|a;$BA3g5eq!uPI=@V)DTAF)1#@2v;nd+R~?-ulFkSf9d|<BC|H!k6_#tWV*~d5Bn_!uNg`7AH)xtq19Q-#_>f-#@}P>%qS&!To)R_}!7d`JNQM_x+3?@w+2@nLpxpN9GavBYt;;?|uIZU-ldEyCd_+amn8u;mdv_es`oV$18t#Hl3MiyYHlL)~EE%dXv6cZ^oDRo%GE*m%dr&()ZRazP#_GFUKYCJL$`M<b5Z7IS=x_lfL)8aiG$Cx1IR+w)DO4NqqV5ZRwl#fj*BUyW`~f!rv+S(^QLZo)@HVo;##(o;xD)@O&YC^L$}^`CKD?ncqCu$ol2;j`8L5j`U4EPQS^nFP}H1Z=N?Je4aOrFP}H1Z=N?Je4aOb17BL;)+wKtg>RmhlM{z83|;T+&-Kzb&-KQa&-K#xp6lN@9?B#3F{JP97fGM}2jk0q4C%`}av#HabMhkhxY)mvzPBGD+p~XVe7S!meeb#p-|Sy``NjT~^u6mYe6xRLe6t^A_NApS$1C@>BHEk%C{sWCR5HKZ?~=aEFZa9rV=69jkBfa*>6`sh&lmfy#+Uo9o-g)YjW73IrEm75q;K|Jz5HU|)%bGXRr)f&+;<I(z2^E6`_<!~U+T6K``f<B7enh+zPG}Ucn>9f@BNPOy?uN9i1$Ilm+d3o*9hO+_mjRDSH$}oncuwEF!Lba%iu@6e=+sT_bkSj?@dg8`Q8LS;=PIR<#;3Bo0vM~dlOSn_<NIf+1}2cs<UBH(=v{uBfk^v^z0V)YF3;2&#3*?Z0`pD)vMVCjT`>IuVw?PhLI}XLf?enMn|D<!lU5f=wIP?Rs2oGduRZD4<3WQ1)Dy`5Srgt@d5e{`ZoLyJQ^JZkA_E}!{H1SdpU0}c{T4L@7}QfGzS^~4m1F#G0q@565dVSd(ijccNudgp?MeWchPni{upwmF^^ie!09S>s@SGtE1F7Z-j42sx5H-K8Pt=3zlYdKEj#IBH+AZoz9x1tc2oBbG#%an2Z?lQPp77|u)5QTt&Hs*u2}{#n%Yy*5$I^Rhl;r>;?a3<PmaBg#=}chEKzY9Jq2gMJ&9ACcZzmB(7Etwj{SgU!C9RD1Nu6=lyl}0r^9NBr%gP*=HFEOuHsp=E&LqX4s8qH<ecYF)An~h-$HM~H#vR_Z3nj_=PmSic)p6UDi)yQ;A9mGReXq!hsScxhiGzGo8+)_=fmSTXFU2LY>q8N$HT)^3{)`(odQo)F<HeRv>)6@#UvGd(Ij|+ie9wsMSIO3s~Di-BeXv}QAKag>&-b6IM$!z{W+$2h>Dpi644oOBAkFuhZEqzj78Tz4IK;*rp+|Qtj9i^x~EdlRE|#|rcuu{&Yeh1r}pX8@ewhDIhaA+9}_c~KdrOiNpKQ68=g&VNnE30%(>Q~a9_9&`Uczw9)J#k2f+Q&M7TfP8%=<F!@bbKa4)zYItU)XIQyWJ;F<I{3w;Bg1<yu@!n5Hy=rFi%*nA{0KbkkG*r;ML`U$*Q#iuI1LKne{X!8}iF^m^+?jp`v%(0E++em+#iA}WIL|e@(ReY;r19}qvM#UE@j-adH<tjc`aS%NK>-PI-t92QCNX20lU!p5u-DW@Sw0;)GhxmMmwwh0<IIdzHp?NKO3|<Sbq2AThd;~s<u7TIk{wTFB<GfYyYV<RBHM|D>5?%wZMOTE?vx0h8FkhyA%_-<|I0ashu7p=|P1bXb4sxAN!r!9@;P2t@(8KU|@Coz~d;&g>?uU=V$IyN7G59ERdz9;c6#pB>wSxXv(BA>Zo)Xq?3U#G0K2zs<#&HtefUbvEGDqK{2jN##bXU<8eGTpkcR}OeE^ue`Rk$<!GTII9P9K-i3t`-q&llkHD$b!@(5~=B`uiDu4L-{`ozX7vPt<V{je~#Y+{<Wp_yYZ1CeG8=)bulPjy&h+`yz3cKDGV`{{&w`&%l@9zpHpjMMo8Wv>E)OicTsXMIVFz!a1?1AMV7l$Iw_<=j=dUtxd!DMLxesZo?hO*MVGyJMy_BeVcxC4b4@wQqfXH3$!`hoHi}cW^fC*3EC8H0zZO23O@ojMjwM4!;hn}a4da4PH27tZ3(wl(T3b@=v(tMDxT!H)~Ddsa2rDN)3k3*Ev?C+xlokj6pIRtRckB8om=r$rTNesa2^%c6z4>Lf%P%nCNFv&)}c8MdJWE{;tKs}y$b7GI%h8Q3Vee$*Xi>b$FAXBL9fF3=(`}Hxd566E&w}dPS}B?&|Gj7oCD1b=YR{L`QUu?ZRS{OQM4dj6fS}mfD5Df(E_mU>#h^3MeD!d9OP}nHEqFK(QWjxHfR&ph0d?nR}u1SE{e8v{;aJf>!Kz1Pci04ubl$u<8T|++FkUY@Ez*BO=$iDy$j!^{U3}+A9K(<@Ez8%=4V*H#=p(6+uRSD8>(oeq7qseepp2V6;;rRa3hXYMytTOO<me)Ee$_JA0^RB@PjJq>p4bC!TQ`foUgSAT#Iw^p@m_6ZavP|8V&1nYjeKV{BS*LibhMq52&cA;svxlTunt)j#uTF=IR`)fj$7&fS*TSfNN7zEus$NXh<E6(0Xtq_+hj@{4m^rsL!0$CtqE(4xCFx2^GZ&&E-^7P;sw{7!~^eC=_Lm^20^YGH?;NG<qLg8m@@?U?1~Uk<eTPtp-<tE2Gun%5Wt#29BZTN@zK_5?m530c$M?mxQCyLU1%(iqLG<me#yzAviCb2Q3KafpeoJ;1XN|%{kC0G?(LjmAY*HH0MN%!#Uw%D(*qcqQ&9jjK3_QxjcF=Tpqq3tpL|mMU+?ZAX*NtqoS;ehtPZBhv2$sdAPcYQk++cbLx;w=d6mBhGSIRqoOhz4OdZ7l6)n}Rh?tHO+~agTunt8@|7W149E5TRuRnyS5i@eeoD|s6>2I?zS88<Y_6X#Dx?*nLi|8fXs&Cb<zc=4_5DygDioS)DXkF|(lUJ3zUE(bd-eGr=>1__kI!1`!|hr}<%rJtpZ;6apML?pxU&5xDS2l0E&K2@=c!!Y27bHNx%C=XgU{h^DwNXST+Y7%EQ`sp'

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
