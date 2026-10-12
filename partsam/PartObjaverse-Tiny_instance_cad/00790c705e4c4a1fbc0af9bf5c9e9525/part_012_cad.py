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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_012.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_012.stl', 'source_sha256': '12a1cbeeaffa308b9dab9b31da3a9597a9cc0f4cc673999d2b4e3b40b1d9a17a', 'input_faces': 120, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15785299241542816, -0.20788100361824036, 0.15550671517848969], [-0.15025722980499268, -0.19921907782554626, 0.16143791377544403]]}
GEOMETRY_BASE85 = 'c$}q}3s4nh7={-SydWruSG=s69t1={Bftv_sR=0J4MY?dIUpdS0^$vG5fep6Q?xWo4`YfNX^vw$IYUPwOSEPTO>4}KTHf$}Nkz@h`QMjfo0@6rFlXL}cRs%V`@j8m{~cnY>>ImF_;izc-gA2*Ia$&AZ6Uc!c`4bs>B%WMzFD*8+exj2FFw?g=<y?C;_ak7X`#WGl9QZm2$2l~Q-cgXvLSV5c5Zf3)|8pq#uS@BEGaW5#p>szCCy5){_g4TAK)YR>+K^ilK<nUxwQn#vi?<{+qArGwN2G=K~<qvH5c|1zO;n?E%>I00O2dX4#GD-l!dRY_D6g?e6?eD_(%MNZ+7&Azj8GEgMEcBYX;#<i{YCGc_aVn2gil)=q!BYju-MLJQTiK;DS6^y@apb4-$Dy+cHq+=AQ67!Iy5P3tu&K6TYe9vdCj;^|Df|dsjyMwM)V`XS@);Qr!l121j7O`30!60>1g{8WAr`4@JB*3%=?+T*PZZ8rE$I-%|Q5;#2R7c(t7q)(ts^br;-5J*}Ig4_{OXUvs#HdY&{zA7U!uzh8@WmrIB*JA^!CH-xWwz&E#vL;p+Gp`TyAtQ2`xPC%W(>xC}|!Z%&}6#bcV9eGZ^K)lxh;VZG%u<p^i%7*orws~W}N%Sus!F9ai1%LTdT^{Y@PVj4=2w$7KAN@Ju0e>F+`o3Ap2I9I0!dI7^!aNx0$2~?KV>$fEs9(PN2zfGhqCdt~B3?QU-<-A^buPrdEKT4mi*~@zYl(V%AL{a0KD>(SQgg4e;rv)k(U_BB_^KOxIUl|(!8b>IfIeJw#C17$2mR^18TC8Cmyf~M_Lid0r?4+cz70QbEAsfjSEk+6<+p6dzO<@Z)Kgo6dTw$4_uSB}Yw}0DoC)7tvKD;{L%dXX9epU@2w%Y*YQJ7XJ<s7w=h>ey_)^3>sOJLaQ|fgU@%N3G!-}ow^Rp}5*DB<3euntME4uoXHOON!!modBn7vh8-^TEzeW}&Bo~7vLm0z&0v541V5pS-6uN7gxsvqyW`S9hs70AD_4*jY6S=S#m5%nk@@GZZsMx9S@qJFo_xW8H!!Qb;3^X3F!315T!p}c=5UBZ6Z2kkWSsB<qO|AM9HrxAJNEf!s!+Bb;TM#0yP7owj5kFajlPr7={9qwQrYA>K~#q@tb9!m}VPnKZa-Vd<fUGUZJ1z5KO@~hh}=-2hVhx~3AboEQUu&!eG5&dkW>GErL&!a!}`4#3#{|<irdGy&#%+Jy@sK*|@#d8*(5Ai4AXU`VC+^r1vU1Bx*mX(9^;=oS$dyjI?c@92a2tW7;>O2eIGB+RRj<%1_pM0E0-y@G!y$5x!eG_?J?!vs4lp_z%NAt}>#4p&5_#*h0aZ9mo;70U+-CM}Nbvx$y;0E4DJO@V?A^+v|$bY8@_gBCU<gZ%?|Epl^*NAwfv;g_fufqNE(H7*XT8#eGpMyoq;GbE9`7y3R{$+?)=H(;*gh<49MZ7jI3;p+6hxq9m5Z^gdcOFS^FTuVNGZ24bJ^VtPQ)+S==R6+%3Y^RG^F;J5aRcg)Sc&Jr;RM9jKL-xudYKPSME$NCQO|)DsAqp1`k9=D{=4A1Yh6bnKj%a%&O`j!Xw>h$3H!}m4F5qS<|la$)*YIQdbYz?&TWR@V-fNf57XCkANe&EzRLNLl4ipn6OKL~dJpURAiv@XU#`$FZ>3q-@7ge3KjoLWFO;M(-JF=C5U<vR>aMTJ9lkte5b95T7xmnof%)$NUmIDB`0(l2Z|MNO53EJ}E$e$)jPC7u^%lbx+0mNX`fX-?drnPi@ak+cZJ&Dm`&Z}m{{QaPIl%A#zB&)J)(~d>4yFzu4<-jueaSZUCI^uNsJ+Pn<i7mc*pu3w>`9iX?Z`5@E!B<Omh4JxNp>YWQ=Q1p<mOaIa&vMMY9n$JvOQHI+mr36jmdUo2WnHY1GyQs1-Tj7h1!PfLUyP2C%cpVs8M7;awK&WIg%Vr9Y>BPkD*Q=k0HlWCy`^x6R9eBA~}&?8z)m!$Tm$QCzDgDGsvmr4C+jB204?OMb0Eor>2vqlc!OQ<Z0xo)Fkp$@)YW1@)U9cHJ+S6j-!qz$C1ZUN0Y~rW2hs^G2{`{2=WN>aO$h%;pBeQSIGUyJ*b_@J;<G?9mt)??WrE*_T-M#Zsd;SuGC)SuH>FnA97E!7xgu=7ulaWi0n@ep}tNIA%{|jkweMh)HlfC<RR3d<RN5*I+(1G2U3H`HVq&TBnMObl7q>C{Mxt=)sx(ZY@o_y1Gx*eEx8N1HPw~en%s)&Opb}NYvgYKPyd?v^P`CeRKtJN{Pi#O$5O+;9Bj??#~~FH<sgoxM%JI%R^4Q)M*1B#sAM_'

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
