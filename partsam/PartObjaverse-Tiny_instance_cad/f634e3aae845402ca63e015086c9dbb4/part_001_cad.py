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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f634e3aae845402ca63e015086c9dbb4/part_001.stl', 'relative_path': 'f634e3aae845402ca63e015086c9dbb4/part_001.stl', 'source_sha256': 'fe091db082f94015c815719623773025f581ceeff0e99b0928d0c5126d1fad3f', 'input_faces': 230, 'input_vertices': 218, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.30777493119239807, -0.05008906126022339, -0.34370332956314087], [-0.10646486282348633, 0.33771705627441406, 0.3416479229927063]]}
GEOMETRY_BASE85 = 'c$}r0dvH|M8NhD>0SQ4sgMhp?N(=!+1fc;USrvIjFlx1h+Oi>RB$Q_oAS8e*p*|3cH8CQJ-3lU>5b_|<2!WL*F<^{&L9rd{&a~5iYG>Ncbo!bOJ?GxvX_IqKXFBc9eDnSC`@VbkW-s~fH#=ly_UoVMc&{X9%-fZPzZXBsNN^IJZNdD)yqsXcw2hm0#5luTFJCH`Eq`)Z)`}Qsn^TgqCRmV@pEB2%lAfEEGS!!oyD7ggKYQb<P5Enr(l5+jUl0_&U~Ts1p!j*xjC<3j`evq1_3iTgkFR)f3E|gkyD!RXDJn0`5XnD#-qnk}eKEc=qsQhW`44ql`{yj`vi9Ft+G+FQt&etCebKRYn-9fRwORci&Rmf{hxF^&eWBIn1A|*yto;W+ZL;?7y>`jweZzklv7RUWlg2)NC)b(yMT6B(`>NjR7yrG+=6y|xl{W7$Ogm~lPu9tU*8VNs&)IzV-FYP$7VqqNt-|L02~&<({nG<a*nFtGu*T*i#ld=Of8eQxK7Kd;#RZKvA2@p`V)Nn2WtXhynZK{edY+m+E!O^tC9O6ed86Qp)t^|`W<AgNoOYX!w%*-g^^d1^TF<jTxy#z$oYZaYzcH?-j}PHr8hzE~{Rh5qePDI0`}ZA6`tvcjo_@of8@gBXM0rPf=80eRPw>2YU)`(sjjkwm=ZEvVCfA2QoaLTh`OsJR>2rH*-ucx+_veW6zx90NuVdZM$MB`2dU|_D`5}q!^*C>(d4A!0AN2klbgw=K<wFnS`5dB$@C!Vz?u+t{@_as#vMzUChBn<e?&f95ZlAxgzdPsrqwCy%2Y#+c_aUyw@an#3-YM|rywT5`H~O7S>-9vL^G5#;Z_XS2%z48z=XD=u&g(wHocHPd%z52MnDe?1G3Ryf-0#hK-TOy)bKdaxcyr$HOT0O6Tu-w%=XD?5>dkrMI-l_7ym9{R-kdl3E4(>x{9ey`bKdye;=MU<_?6zAH?F_ToAbu`ne#^fDsRp^_<-^+cynI&4s%}je&)RHeav~|Jj{8cpE<Al0CV2(%z5KH%z531ne&Ec&KtiMbKdA@&Kv#A6Xiq7Gf#ByFmIjQwHKt1q#X9<GV>%F?CaG$F}#{@npgA0=x3f7{mc{Ht9hb(AM?aG&j4?pgz!;yo@$=&ns>PG0nPil?}q2T>)zqM>t5Y=!*kz_^K;*ge(t-`&wW?knS@u*kuM#0Zux&c+xr}No*JI#sqQ1k=6Bn?f5U@aR<EAFx?hpmVe^5EciOFf%KL5B^Ng(a_J7?UJ=<#YzE>kHR=@LdlhqIEykzsvpFWS+eCVU*#@;@l{4aVMtiJ9y^)~N+`7bp#A6`1N(&nAN%{XfFQJxD%e-Zn?-e1oCufOkZ_J9344<sM4dEb{Y?sLJfzwfmzH8vml$Etd(PhQ^8+lSQqCS)|)ymP1`V)KEjS1#GSFX{Ovn-9&})nfHa3R|t$bAJ65n-6#7v|0VHSGHTPzcRJM>Srf+T7AUVWxY=JTf?*88lL?&Fy^syu5VfG?ZNDs;l&TQ-j}ne&vPN9dG%aS-mg5*1>LLXg3-@&!RY6?pnLUP(7k#t80S&X1>OJA+cN{2kFaOzKFXeH^s{Fg{p^{#53^_L-p`(Cc=k-gvu7HfJ=3pWCwr#u)t+g1=85jrJTdy2C%RYj#PIByhF5#0{_jNXnfmppJyY*z&on%HrtYI>yggI*KK4xGec3aO^RRCi{c6wD@0Z#$b+7hJ{XA;V)IT@1XX;+<nfm$Fo~ie%JyY*jdnP`hyxcdk`g~g&7atzGc(CXcF~~`Da<hAVRVt->8nXSX(!BfryRS-TPXB+uDxD>+VYY~Q<aGE05kC|0WAb(QeGykh9LLMPYvkkbae5>l6VbzQJ$T9QiRh-@O-=Gq5na@~s7XE|qLX?jHOcRa=%C&~P4bUKd`A5<YLb5_;!}B_@v^U-9EQX6NPb5|8^^WbCBH4=iipE_+4l+gFnpLE$#03c%yF0Tk`IY!rQS+S@|z+)rv5QC$p=NWP;a3o`3(`x)SIbEeqF>*MO5HrUlX|kuAoP9nTU@>l;h;_m&oOCIX#kJ6A|IK2ww6JL|mkPk(%UJMO>hMftut4A{wbTQj`3B5$CC&rzZIo5$C9%qbB)f5e*{t<7MB6<o)n|dL+Lj;;e{$IC=a}$ot@Z^hkbD#2Jn|gO~h*h<fVv)FeMI;xzTs)FgjTL>=`yYLfSgsHI*@P4XTQ)gnsqvag0*3YXF&`8g4%IPMf)a!5oK^(tzTPl)(j#Mj8_u>709PW?JH$umXF6)}T62fkm#eIhE!d*OhHY!O=t$=k@Q;cf7Cat^#5E+Vgii{KsPAiM)ECg;M%a0&StxCGuwUJLJpcaihpUGQ!Z&yv@X^WY64){Dp>&xfapxX1BcGRMHvMcgZ53VA9#gU>cZu7cA<oWz~P&*2#P{*%dh@MJiZycSM{Cy}3lC&4M?TsQ^3iyVaSf|JQ>;AD6rIR~By-$`B#-wEGA&W7)RlgI%$3HFg!!9I8b`8)6gcs%*r@OXF}`Du6@JeK?|cq}}Iyb>M*-%efu-wux^e-j=Jk0O5q9tDpiKLwA3ZzDem-v*B$e;pnHCz79l6X9FQkHfdZw~!x$Z-IxCv*6+IF!H1DFnB0=IXo1;nY;|X86HA@1Req>kTc-~crbY>JQ$8AFM;FXLFC2oAowQoBKRhFAbBA?5FS8&7#;w}kr%*maDVbcaDTWT`9ZiJ97}!xj)h~$emDkp$QiJlAK!Jnc_8yTSk4MLJJyr$hGlG^eiE)CZ-lGhQ{+wXDY%-v8LozF$XnnVxR#s`*TQw=0=N!7O)i8_!}6J$l^GM8*zZ66mxX`7Lhiur{T~?gBm1uJy^owG{+Rx?%x7iB$$KttOsw~d`Q%Uk1m6qvH~'

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
