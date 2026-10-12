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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_008.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_008.stl', 'source_sha256': '456a34d2e9f7dcc018afc84f9c50d487c9564cccf3de7618b2f74aec83a12b62', 'input_faces': 226, 'input_vertices': 230, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18954920768737793, -0.4999997019767761, 0.1068500354886055], [0.057330422103405, -0.059321410953998566, 0.25275498628616333]]}
GEOMETRY_BASE85 = 'c$}r033yId8pm%!MWl^b27}>KDx$Vx#O@NcBq6cyBqX*`At7ii*P5ucp`}JiqM3*-#?rAxu9EsbS=FFOBO24rQ>w#s7-e+6d*1)Oz2}X2o_S`z=Q+>+=kNXAd(OG%I~(C4l`7X(=+i{`c5b4>ua2S^<yED&5+5BqZ^o49xHhxrEb>tNgl~LI-7<K@pztvsO1zTb9~B)pCDy;I!@v8~&i<_&{!?RO=fy_Oo)i-s6>a$aB4@=#yZyN7k#nNme{RvfL%UXv4gswkOC0~>r<zfR=0VOJx2RR0A2n2a{>|B5Hb3R^72!M9j6H4lBRnPuzijRC9J{Y-zDLCO_Vqa<`9A7l@x8NZw&X`lIwbNGwiLcL{^#9>>VX-zMSULbDzy9BXN!fe?0T!n?kf!vD8ADyDPB(x7rvwXg`8*p-CLqQgZf{R@+hZ-@A&D4<g1GpQM@b9CB=J%QGEPFIZsl6@U`YKQoLUC=bNJ4S3D^GM(-5iUp*-5nexxfLdo}9P3>wDSS0zA<ES5wPG#}I<d^(i^0iv`M14|*50##)o;W9beaUUfS1!yIzS8e=mlXea0QoV)<oa)KOZi*BE5$2$RfJzQ(o4jvJxeIQ^sm%Ek48(r^8I<L&+RWIU)vNzetEu2@;?ry`dkhb@%qC`slvZkDEgr+q;8?)_f8YO9$#Ky_m!O^D1O4JBD=3H3!wO<HAQl~Pl<T$-W-?R*V9s{AH0KP|3)&^e|Kb_l>bmTji2S;I;DD+`BQv@Z=`mq_pgibld^Cv^^a1Y{Oi*wPsBx+-B&jBr97_Q^uB!CQT*fw<UgGv`{{YYR|kGY`Gb2<{fA!>{Sa}cd7<Rr*)H{`<v*J!^{3@0H50yCZ-L~i$$p|gwR%M^yRUWGN#p0_<UG5t1Z|W0+49pz(71Z|*eT`z?se*){nw;+DWP{ne=1wv6TZ?po9gLH?^nNm$7T1G>{QDCQ&^te*K*#c{H_sFy#7uL>gRjsDZl?C^6w|f@$l6JO{u*RM=3tPQksbW&R5hYV%v`{$#1xy>a#yo)JMy`D}3e1eR?mcSp||`Ri}9-KSA=<tAR9cRIX7h`EUBrdu;!p$nNVu1kn2`AL+9D+T*iSpGmiz(sOIgr*Rc^Nv`Mo*)*@7St`Zr>%A$yY_JrsZ9hr#XOBnpyIAz<9#PMYf1`Oa;e3JJS2i9ezrixeSHt>{KfZdg<d=BSdNJl^k=@sOwifMGvuC>OzP9)n)&EebQ+n=(Wi&56%gvMW4~eCAeV8o8>pf_m)T(ro;<cI=sJ#y!(0B-rAb-spqCP1z5?yv*2|PgKZR|6r6#sT2`P291N%4<gqj5O45&2tJ?y-;avdkAw$<L@p_1CJ=@3D9@`KSG9d?xR5*?ldP=Dn1|Y4jdH7?&>Em-U>++ran&yRU31rukuGkmPH@{^U1pT`c*npOuRIoomVd_gzGN9O;c*c3=ImklNd1k5hWCg7>wwpX94aQB?ml&wMF<(^Hy<8zsu^+L1|qLQCqO=~3jr_?gDrsPzSQUt5<;zpoktC0`%Xp61)gmc>$h=@V-2*{YJScJD#I$D<uxcHdf0KiTV)@}FBy<8A$T$v4+orSZR{`m5?=(JqJIT*+6`jtRf)Ni!Nh16NX>unyG!=KKa<-9Y=Rh*K`7-B*5CNWOQ8lt*c;Nb{|_dNcWJvS=KRE_O<O>2s>*{VtT}!B+C0bQJX|Q|GwszV5f0#)Ic&${&!M@v?Z+=ka>7E8}JLv3y>iqH7s1?H~9R`Uif6{xN;lKU&s5GF~>`OrMW8E1r!vE1r!v)92&O^!a$R^0V<~<!9r~%Fo7|m7k3_{hsGup=>@eeLkO<KA%r4pUo$h&*l@;=ktm6TsEIr@oYY^;@Ny+wTsOsdVg1@h-dSy>GSzkS#^!#`Fw8rY(7^CpHd#azQC`rzL@cReKF(N`l5Rc-6#5iuh;M^tk-5dU$0G{uh;M^tk>`>tk>pq`Fd^U=j*kZpRd<uezsogL*`R{wjZ;6wjVQnz8|xEwjVQnz8^Dvz8|xm%l2cI&-P<hezqU8^0WPz8ZvUf_<OcrwS2Z;RUS?wpYMm^SJ)4i?WB0VKZjpoe-6LG{@l#N_vZx-4+x)~cPyWscPyWscPyWscTAt3cTAt3cTAt3cPyWscdY#Eyko_)^N#A>lH%EU(DK=NP_L_!&(52s&(E7m^O4jpb{@BUb{;o<ejYb{ejfiNUOtbTK0l9JK0A+F`Pq5gswX>-Tk-5Xt^}>1{Oo?i^!fdU>GS&y%V+l+TF-h1MSgx?WcvKR$n^PrkrmJGi{MwdFM?m;z6gGW`yw-*-xrzB<@ZHq9(G@(&lpSb>^{)+`F)`2^ZP(654#Vv^050rD-XL5G<|*_XvMSpK+9+MfmVI&_krQkZSslZCx_JYQ52(iE47uWk+!R3!!$mozWgeAM#ul|D!F~9|Mx1{1J$mCVtgt?J;8>)0&eUsRTX3VO2y!sP;YQea4l#Pa4m3KXm4;^a0qe^#B&;hdqJbYy};w3%fREnYoWgfuLY+={{&74=R*Gs&IOl3uYya#x1lG&x4{>oAA>J~GoZ`C8Q^u$Y2bC>3D6L52>Qoh)m<F!5{zPS8>kn!4Y&rh3b+Q?584Rq2W|!J32p@*038b+0FHttfuq1np`U=4f_FeKfOmjDg_eLn1%Cnk3j7853iNaE74Qk@AHXNTJE8A^cY-zOc(4YZ3RS@>`r6>8it$fGiqam%;5yLPz;(cNq0PZ{!5yLfz#YNi$T<klX$lU4&Hx92CqY+&CxJIWcY`;8Gofd|nP3<6ORx+4HS`AfYj8RAEVvw;4^0E-gAYL0fDeE-LuY|EgC|47!Qtp1gS)!RNO$RsV(>6%EO;0=2D%U&15SW$1t);FK@Wqsfsa8y10MqyL(hYY!Iz<b1YZUphkgJ)4*m$b2>cOv3EJ2Y?d}S00sRfQ1vmiO1snkG1|0$J1|9{S3myfIgDwFtL46Ev=Pt%l_d1Hf)u6uuR|ES%-vax9n?VPIn}PcxXCFML9XJ#^5gZDh4qXqP4qgG>3tj=<1$BaVfloopz^B01pm)I6z}KOdz}La2q5Ht6!70#9;1uv`Xe4+w_;=90;J)Y|gFCs)P<QE$V(@6_Z18CCJm|aNdEj{Hhv0Z{GV};I8GHy@2tEYXp+#UFd=7dPd=8ui-44zIZ-FibZvihr8(X5?oxt^>Z-VQC8$f%28-N3$W59vn;n4Zu;ov#Y1>gm!kHH<>rJlRIfnu;P^w(ftaCPW!!PUY3&>>)daDU`{8_($g4ueL3!@x748^JTdtDyVAtH7zyJa8&F8+sR<4ZaEe3-~7Z7PJ6-3!DQz2+jfTfxZvk15Sia0VjgrahLEA56{|_{?mWa_~oOC4Xph?Z18W&+j09h2fK4woAdCHSByQ8d$a2)Ccji;hpPM=4#Il*'

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
