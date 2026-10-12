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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_006.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_006.stl', 'source_sha256': '8ae9c42bf15b63ae835b66e309c6488ab3572ed79da1bab762a902960265be83', 'input_faces': 239, 'input_vertices': 159, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10335331410169601, 0.14542676508426666, -0.016939908266067505], [0.10335603356361389, 0.4183275103569031, 0.2056889832019806]]}
GEOMETRY_BASE85 = 'c$}q~2~btn8OJZ17SyQGYDI~cML>Nn2pF(Wxq=c?5HW~?TOJAsfw%y&xP<ElxQiAL0ljevXsjq0MPuZ}UE(C##I?!HGpS9|aVEBQl2((kobUYa^Smpa>9lX=%>VcPeDB<Izw@1Q&mH1pTwHrg{NpWEJdM1X(Or^Q>nin@^3!tiGUun|4qv#q$Vuu!KKtmpBQ9}re6o|2FD(y9P0O916EH>&FsFwFnB;);MLBsnDGT3Rl#`mq{OFYI+_ZK-HzQ?nTKo6FpwMuW96Z=0uay7Ck4O6uY_pf1Zf#ek*Uq*GrrU!~FqH?opCaG9`U?B5Jsv{7l;=dgq{lC6t|z~7Pm9=(wrr}EshVAXlKC?Fv3>eQ15@jQ81gOfrG8EnuSJh*7W<bv1(%AxMfd-7_5$_)XgK-SN~c@odmJtmeVgu^TPWUgKBS5I*RLD)%~sJ@;mcMN@Bbg3$LPM2>dujGb~z#Xwwn0MynpW7YW<GV{UY9SC7@CCt$Muf*IjF*`$D`{zxs^mOSL>+g)f<&9cI2}esq`eA9?#M#g869zIu8D_kZYrp0vv^hbVqk***IGiI^4|*QveaTgv?IQ2)gXE>ZmJJ_l)>d%mW;seh~D^QPQy5bw+SZIAt;ua94Ger6SY{eCTmc>TU)#9Oix>nVP2+D#hg!hKgM{`>L+4)t*R%eAe7ufn(9Ddu@SsFJVg^S)&w#p}La4{BloA6MR6JbtM27c~CC-u$}hN&LFQwA(Z<ON06RUdY(*P(MQwa$5!8UO$^JQa-Jf0sF;%tf_Jn{qDPa`zW9A<)>3llbUXluRR<?^QHDUMEQ{_`;o6&J|N%Xwe&;!`-7^z)KB4hns@Ei4>a#uM*h1LUspi$t0bFvevWn9BaTOk2>XNR>*G;BY5Rze>*#Lk$IXY2|D{<xKkIJPIMhSR>|LU-*MoHQ<T=r|*S{fNuLoNr;&W=M$xq)w^`N*;Yvc2>yn@!_0e_k=d4DsFM|QGqr~YjhdEU%l(Rxw*KP#v4Cru<@8RPdcX>cw1n&)-On>;$1*1PPNQtmKcbG~d4eLX))+fS{O=a`ahG@kE{@O5-?24AlUNt>vjhYb{Oc^t&^)+?FU<KaT8L*+Fy-!DgRETI0?IJ#e3R4*R?_Z#^Xe<y={)#YU#f8^&oXNCMr1BO(JzI{LW=h*Y2ujgOw?-+02XAJT7I-h!|q*d_sI=Akuxa<(GuhXWaa))^Rx!^tLiWqNSr_t^X@%lQo44UQ;ug{Ccy`<hD5Bj`3=Fc5%P1SAcXJ{_<V?FcNE26K3Z|42qyL(mi)p|2u7haVPzWhfQzK#M`IP_zUXdqu&_2VUn>n>@gx>B!pz2Fev=tXsCt@_GgoXWN1d|jtDQQfMC@8m~xFz?di@`8vC>cqNu_S%RJ>PpFeV^c&2btpY4-4@Y7-72?(%Ok}4AGE$f^zHkVsVCpJm1^>h>&Oy(jeO&}(;7eCPW>9zsnlm>1;rWGwI%ix`C7CG_p{#P^{DQwCN=C2YPa&52w`2Q*QZpAzP>Kx$h+r6Utbs2&m80Rbs-^MJJ__F{%+h4%RTmpdDHh*-8b&5ic;_{eK+jS)~w3C6mQtimA5_jQM_UQmv?@?Pwd||Dwduj)+X*7pCekdyk8urGR%)ZkLHAOUtjO8RYk3WZ(r}Dexf>;AND;!zrXa&=j31ROn+CV$B=Jd*KwOmTLs_#{Jrr$-|uftKOl}rf6iK}W^-TPPy9_~t%7ggPo^E``_GdMeqF<J+!{5V_K6qH6*c!8#5%E`XW+kZo`L_uc?Q1mJfq3J2Pxigj<RgqcZk$@?)v%{@{Q*-^&`*2q=s{y<|0vj8P9?8iJ&9&`^*@=ULqIr^GM%NI&VrRHOhm0Yd)XP$rs7j&$qTd%g>0ueqS1V?b*Pi4taCq{p!A+9|gYrq>}q_Hp+v|H-XQ)cmHGJb@g+#?i<h5TKOUJRi6jE&WGk+Bz+Xp<WRRb&+ESNJZ}qZAYWFlQvPj87Cz5sy_@-Zyhimb-&gs42M#CS_<o`L#`g<3Z(OrO-QxX4_l@r_w&f-Kx*wL(JW8v^(f(j*xN)4u6%|DDW%YS<iH|qo1JapUyskEWOL?$9Z6sguF5vt8+zHgb6#p0gzT!KU?=#oW^7Bty^ht_Cew0u6dB*Z*?IfQMtoPdQdEJKvQax%vxAEs)&ij1de!8y3VO_s7iRxb-u#0^CeNg^1hQANqe9$81QyYJm)~Dsif3=8tlgD1+>o(T?6!l|x54Gi5PK*6mv2UmwmYx=`OYgJs4sYpdmel!p7fE8xz5OjcJw<p$XD0jT+VLxTX2^f_iasj%|9(ZE$)>QqO@Ri3r+`DC0pJj@KeRWP>C0e$a3Hi7I1oG-`fKoDunF1+Yyt;C`-7RvV5XzMLEtfHjLp#Bf|<S!HiLhM#&|094e(U(Ea+_TEO0LLZ7|b!z`5W&G{(iyjbNtbV5Zx_#o)Ej9pJU#Qt0o&rQi+FDlpS+;0@rF(B<Hj;7sTOa3(kzIup!v3OE@Y2MqzofkUDGV5WiKP;eM@Fqo+c90m@D27!Yx$Khy<W1wcR8S@$goeGWtCqQR`6Towzx!_#P-yAf?MbKh!G3KTSjqx&QDYz7Kundjy3g}Ak3UE3!6PylCf+mBLk?SNh#*?9;;85goG8*GpXgD|=d5J}1JPn!vPQd+7Lt{J-S_Ce_z0E^ooCaM1UV-~bLt~r>O#&xjtclQAa4fE!2%QH`gR<|7+uK|1Edx3qoB>XSP6wxgXFy*A&j3$?js{NxzX}}!eib|vjqxC;A9xVhyS<HVZ|oT|7s|emfDQwX0QZCT1@{AYhrR^v4(<l+3hoB(3GD&y3HF5k2J8tQ2^|g|309!vzzR48`X)F9TnNnv7lKzoRq!fs33MH}1iS{i8oUNv09^_$09&AQ!FsMO7z4ZBdNjrr&=PP3xE8twTnny5V_XI;02kmoWoV4Epb_9K@ObD5@OZEf8e<P=KQPnoU=Oe>v>VtJ>;&xzb^^OWJ;83^F3^$SE?{4%0`>(*LQ}wz;B06ixDdI{Mq`|V#&|2V0=yMm4Xp)NgLgwK!MnjV&@ylhcndTOyal`jIv%_P90m0OM}Y@GJ-`FNouIDZPGD!K6WAFnLEWV1AI2`wE?^gMXQ(f@GuR6n3HAa{fM$cUk?RS#mx;JnrVGJLHwk&zggi0bCFE@v^2)SM$a9@A7j>8`raQq*Hw*K~cq?>~^nBhIVXRD}rRQ}Ljqy(adqD?+nYs&ka2Imrj$B4z&L*NUeg)bI{0jJ2P-k#_jFWS3m;dx{x#u61CRqF@o$;5BuL|NX-)ry7{^AfH<HoMvJ^*K$kP3DJmi`UttG$5'

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
