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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_005.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_005.stl', 'source_sha256': '3011391c80c9f3f7f514829ca07bfba0842ebeb3bc46069403540a14dd9ac5f8', 'input_faces': 238, 'input_vertices': 163, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2410099059343338, -0.1314946860074997, -0.016636937856674194], [0.10303425043821335, 0.36915138363838196, 0.19006793200969696]]}
GEOMETRY_BASE85 = 'c$}q~2~<_p9>xz&42~%lsOZ5oG!+%ZP)KfyWFmqiPU#`MD1x9&rbHcwv=T@h07c|FrYV}>fW468Y?zf<P7UwodZk&tr}na5*>Lx_zl#UfduzS*-gWKu{rK4TzyJHchjY2cL^f{XsmPbFa{Prb-?Ob1MYI-*r;=q&%Sep3ru(PNTj-*+fiGT8T{C(@RLo=-B}>Wnn`uptPxBkB`h_M0`}J1+5>nGL(&AEPq^8ZZ3O^z)Io;~;(`U!cvpRn6(SKlIZ#A%IZ#75#A737h6l{rC->-3~TAh4QsFswzJ51zOauU9gH1GiYqe&IQxBcE2zU9&Kqj+DR58e{KaqHfB_@U>j@xGj(1HxBVegWS&fANq|{r>eWh%;gve62jCQmB$$a7g%;%VXgyF`ptI!+Y)?_){a`+h_j^`RJc-+>bm@443`isH%Z(8iD+6k4s;7{dp1I|E14fq5A4@nU5uUmH62{;2iQX8ugNKj3<%5GScrb{J?eZq5s9NnZM@_;cK5Rgs=F_MLw2=c?V>k{<8lci;6Jb%_bPf=F(I4Pn?>BI6*fn5&vo{_}Ue}D#U63?0V#N`rC8pKXr-$&D)1@)y(tK-{Dg&`#*97{#TXo_0D0ar`>BJeC>%4`1b494@1Ar-i&d->LmS-B9Xs6<3-e8Ih<09_-<V>AN|8rSqEzjeB;M`$VWf*`!>w?OsMpK`tBh5Cmg}LXyJj<51LehxT-Z4`4)GV@uTO;I*;3hJdIi1q#rf-6`?lQ?~#x3_21vc`{H7b$?<Of1v;b*zUGyWx+xwdWvE-$3i#^Po=1?UTk=|rKPU^n(Ipi5*=Njo2X%ALlzw&z>R?o~!F<(+romU*zJ+?)zJ2^{tmFH>GM_)@$o=Z_kDc(t?w-YXPghnW?^v(n_<h<L_-d=aB7b#S5!PJ`Is{+4@G<JCxrJbTEycMqPF81}FPnEw74qNF6u#|)%W|L0a>Y6-?w_5(&s#?wl>6{8<fYYYgRjKu1@I4K%XR!_HGHGZ4SCLA52!)@qY~lUs@G#3wbPqy$aiYI>_6=k^0fbOZx`y<EgHT)za`F{er7qwwVw-={nLGm5x@BULi|3tBYd^*4tZXd-@v>qoo<}Q{JmGn_0l_F{~Kl3;2V=}8i;ef8spjmE8r_%SD_Ai<tgk#<LDOIf3dqfFGr@J&gwlId^IHpz9skCK8*WYDSUfr2+p<r-gmNpizTvudEQCv=O6cCJ?$kO;OmDDV4iyIcPF5I@1DYV{hq@4GQ5uCKC~y?hHrQ4i9GGMcD#xB-44OGoGn6p?btP(Gi6N$d}GSTa-Z++ium>|h0=dw66&L!h?DC+=6M<4D;fJnpA#$B@y-mH&y72BKZISxdfHbGka2udR%4wj7Qk1B{&o^^=5NM4EyLDf-Syai!q;P>aQ_<l>yVdm?+$$9%3VAU^g9Pj5x?=`lXAbkiutM@SLAx7<-oUmG6wZggL85IRO?*$w%5Lw=OpHqytm{0;j72C<zk*|+s;G$@FOP>|MphYSGzU{_0g2w@U_$uoKO4QH&Iu$wh+G2!)+`4=Pa0?J~C3q`E^a6JU7oEALEq>_?AmgW4~#CE5vibz9dlg&xx1kC#N;$s}}TuZyW9}>#sMG@0(J59QFKo3Z6GglV9Ziyci8%@qS?j`j4B0eXdmvhp#Wcg?cKV=VM;V?P0Qi<=Pz7BV^Ybs8eYOeA|%g^4>Y@CHG5*0QlPZez;Hdp-XWeYO8w5IHN~lKKe^Z_`P!Bmt*i(W}-f}?IUro8rh}rwVerA4<p(e@s$M`vj2wpn2#R63-_mGgB8A>^#|f;oj1wne&cBP_F>bIx7M^X*3C9J3ck_*4*Kiw6&;lG7$)PK%h-<bHWnbhGNifmzkCP%E$b)a{Hep;WSrJZx65;wDDU$Rf5tgCwj7iFAC8gFk=9?xdtt;!a=roK^1hmu`8L+QU2!e?ukJ6;cZ3GtD0I1m_h$ym=VOKo&Y|M$pIV9eDdWDcGWWNnpOpT-vMO_Y+oCbpC-%IR@?Kznr6LNxC2NN4zof-w^yj$xWY@!H-}rnw&X+M@?;*2q8Tp>P2ZC$y+%i5`R6ovb|4MV7ipQQ6X1^|<&?=lG+xUtKa~$KEM>+auC&IVW*D`;Q_hhFd`>|h{kMjG40<*6<^MB`Od4K-+?jCb|Wy!KKv+s;=Ngj%OLfNHn$NqQbnLm74jmdZBuTNNT2ID47g0J+k)vJS1=(o-68#7g$Kco7Kt@ZNnrpMQqd}sca-}KY?{mpB#KjWysM&lk*2CBAt^9mW8Z}y$@GOk3S&dUClW#)X8u;6mD?~JdXt3{pFZgB<m@_+WToo3(J-%|UN+z)&2UpZ>7TZB9MIell{wC>~2n)}z)q0_p>=Kjt)=%YuSG54>V?^ds6X1{J7)9#!!`_B9|_vLTY8`qit5AwWNE(c;C)y=p2t2@npUHyAMB+plYN13_5vz|`BVLk1ox8c|2Uvp`t*>~ozugaA9Tgq{d)YZqWJhjH;*X{GS_G6!@#TU1l$F&EHlAk9d)NSTGEq%ISA6h0x;$Ev;uhDrcYD|9JKEJSA?(<6%x0~bCo%fj9J@w}0JYV!1o-fNt`T4!!`E~jY&#&d8wZa_7cK4S2{CjLqg?U`<zBlS`>)|i|?rCuUIQ@qAkD5?hX^!KZmwoe2`T5&<9zQvbeQvp+95(yvo^;%k+TQ6^X5Se{`Ss<hdi8v91on^q$yZh8JZ(>1#s0LXYj2x<JQrf>eGAa#(UdVen=6WF?uw_95NG-dK$zm?)PMgKK;nS^>MMYNz~KM)D}XtU9G-Kucs9XtRE;cjCOM95r6!SIakS-*wv75Bc^P>To8bA>7sx`NC(kF(WfPo8%^(ZSBqx%S*#ys{W|M{Hkmr#XvI$;FeVHtD1$ilXC7a;2)K|$uSCQ9}*Ru)UNL@n~`Z{?dxtLAxI_hiW*I3_mY=U#C%gDLpC2WEhP#2LGkW;Di$*JVo)Vbu@<OFIWIe|QjnoOQWPNB{tr;xL#3&~mJ#nh$b#pFEdN^%~#kh+#!NZv$UPu@f>qi!UZkxQw?<Wh1Gbsf2goKMXq=d#xMY=T#_3D&6#$T~Tlno3S5CsAjUlgL(T0@+HAqs~$uoK3;;)D-2xxfVQ!nnj*NPNOa+r;%Tx=8<0_7f=hy1>_CXP2>&a&D1jTX7UzlDR~RoMlB-S$R*T#az1M<c$lMwJK7*N!NJra<Y00TwJ$k{+=J>%?m<?m?Z_&*J+&#hJ-H>-h1`<tN>#|N<Yv?+<Ywd+)HdW6WKU{mvM1Sxa}QuWhLJ<5e&kScKdKMehj9cCaJ1g0diG`vq20*=WIyU7WIwVG^&zqk*^}yK%HNIi6WYi$-$ty*Ag<p4Ho<|^AaWqN548um5BV{wN`8#of!dzjf!vnblH8Wuoa#z$PHs$XMsCLZ1$T6`o{sh;o8V`tVdQ7X<EbOb<H?h#W5|=pli37Evk7+Y0m0$ak>qgl5Na5C2)Qq{C%G@#m)eo+OKwMPO>ReSN_8hUCA&~P$S!1s+Dduw65NF9O>RPNL-i-OA$O)mkUNvb-VUWY>(h@l>&HIPtf$b?)Clru@=&Tjc__IT)tlUl+?Cpj+?DJ_^&oqZAEvsKA0~I9wkCHWKThpP7WyQ4l%rW3Z5*56NNRs_BzZWs8+kZ+FtrnTFnJ*LQSv}?2=xha2zdncY4Qki40S9yhCGoPOP)xc>S!|@?O8{gPMu1gPM$`MB~PJFpvICXkfW$$$x-B|L_U!&jXWFwr~m4E@X~R?oB!jl;XCX9d0>8LGsotw`(q&{vMHVmjU4~Phq7<PiYk8sntC5u'

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
