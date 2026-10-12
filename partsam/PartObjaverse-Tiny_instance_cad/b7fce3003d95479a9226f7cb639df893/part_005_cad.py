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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_005.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_005.stl', 'source_sha256': 'd86ea218a6aa0b3fcb729a903ba2576fe2b3990890eaa6c03bf73a624f3b2672', 'input_faces': 342, 'input_vertices': 206, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22149384021759033, -0.24436843395233154, -0.4449480175971985], [0.21979153156280518, 0.08387333154678345, -0.22154447436332703]]}
GEOMETRY_BASE85 = 'c$}r0d2m(L9mg*aQ80x-!e+5NmdawZG{l8P@<1DQ4G2nDWDOw*AtdaGJV0cRK&0#v!V(BeLPAI|Aw0GuKyX0?3$;?Gtzu`|POIV{o!WcO``p95C&wA5eKWuLe)4_i{?70G&be=!Bn+w-7G;GVZLPALHd8-{v@8+fR+Ke2DSdXzq@;|;Q_~jIu_B}|9*$-`KVnEiVjXL)wW#Cdq>M@F9eemX_L}l^$7o;2DKpb&r%y;7H#2>5lJMgvOwUNN{fwy-(vs}IJH>Q;GTPUzbF^=<?|*zW6gAvQtT`iecfBJ*gYg5dpE3CU2G4xt@xNNT+&CWJ8Sjhla7zB&{jPjIU>&;Q_N|`RE(;x>5_i+&2Onwri6>9W{);ltS3_@^{OsHxJo8#7=LL=V@%8+HnfuG#bp~IqUlLkh$pJa;&r@%j{NTpXa(%(iGK!_2(MbA%A?0#>;LHD<kbdC11976Bb+Ja@7xC?<GEbM9kUy{A`<{C6{R`)W`rV+(EtBv2-v6=3r$7Gt7yjPl-(Gd&n%fT?&pU0(@A!It>zlArcb$Rz)4c0iJVLHFd(>kg|7O@;cOP`$>4Wlz|25Az9^V;novkX8`bEuN_q@t)=gaf>eTzf>KN8d3`>XrT{#t+BQz$j6beVg9eJf)_esIDbcb&TL)T#VsOLE-xD8C@>u+dM;JYvj`@8tJS{HVZmU+cbepDJIwuXSI&4wURJF!tH;wLbeF?onXccimU@JHEE>y6=p?efw|urt^0D%cCKG)JsL~{ndSS|N1^WX1Y&xU)`t0`O*)}eebyYJdA%V`KTP9c&yN!NB7lvm@(jp$EW^4<b}i1|9eq^JCE)=d6XZWd%`##U-d2g-+9ts)#|vXZ;s#T*%O|6reDjI{<#bJp8T4x>T&!&vkHuPKD}eke`<cQF+aZQTg}0Jruvny)gRpY*<MpWbzkkT<7@rYeP{gm^T{FKKY5J%JOp1Iz1OtA<2R<{NIxQJR-Eg6>b`S6Z@=Cn$8@fAU)@Kkx!a`w;I({rJ%O(iH%pCfecXLt=)N;=;BLh_nP=eFJ3V<iJQ|Sx;0-%Gc{E?WepVN!n(Ehm^?JUpDACk6t2CmoX&-f8<#Bv%A9Y`i4}T>g&Ty`jubnGv_2k9U*X|45SNR=ZyDyZl-51K&?hD;l`71}RHP-L=di|fz&x|wmQ}b1R$JhI*`D%RoejDNp`xw}}Y?Iqp_q*n+JcYgF`$Vv3v#auazcBo|+qd?#4V^Qq?eE;a|Jl1&WZo|Z-7xvVvN4~y{lLL`q48NQZyNpSojvsghLv41<#&8Nf3T#g+LT}UTK-_-u4>bI{bvqUnbsSKnI`@0ezQFJ{XGU(%KP-z)LTaX!~$=g0TCBW<CU+C4@P}+PX2wgjmNi!{_~uvo<QsCXXSeREzEwaPM$tkBV*5)#w%YRpZtBfyPja)F8Tgl>vJ`}ey$w9*5_@_SD%NS{MtEG<F#|B`_4IWeEl5O@;N8U*Uq8t>-qI_Sj*S)>*r9_ubo3RuXYaAc<mh4@;O(^*T27LzWV;+%&VQ-TE3QFKeuWhwR5ZTXy>+;&pA|iv~yd_*T&cS{-yb~&fAZjbM1Rs@ZI(m(oZOm@ALk=un#<bqedI$dOQ8$s>grLlHYfHhu`;(w?2-M{kuKDJKkRyko&W8g?D`EcdO+(zWDq-xo?dxT{6|9e61ekYxO8!t4H}-J<8YW@pt`8$nQNROZM%~x9@xWf{IMJo*yE;<7+O-&pW<`hd=Q6R^=0Ne7mfx9)JA$g+jA;O!JP<p14BRGvr?~zZF?{*;J46wR)7V)uVi^9_4HGC||25kXL@$v|q~C_DlKNekotuFXe0drF?C_thViHO!X*Vt4H}-J<8YWQNC7>^4;|$czz9B@TcnRRT1_lFgqGpQPz|RuAc&hDISiRe+o>A{YgIsc8iVqe}4)ruxmJOM;;;gFj@p3hL57f@KHFQYmbOyNeC`PkHLlT2{a$hCy(Hhc9gjClu(P%Q}A)P2rYw);9{;VB;QH66g>f#!tbKRa4~rVm)mjLmFG0I2t5Orz^Bl&@F}>AYfH&j4p*S>!WD23ErZL*Be>d*OLm+i1fNH*z~|wM=vDY4T!q%aRd6LaFECFvd>O5TD;Y2NDEsG}6Xz`C!AH<z@D*ykidMtb<hzR2z~@+x)3@{V{yghBO<bh+7g^64qKe*CQTJJ*l75!ccc-5fthIvYFQAoh7dz_M(HXVi&hVpXUHDNr8m$LM!(Gri@XK}#x8r&AX;^3@SZF(VgdHR8c!?04h$g^^@KDA)!F40xSoCLbEF6xug~MSVIussCejha@u#N=kc$pZ<nnp7BaAE}O8^PR96S1r{mbn`d;jBNLIolD={66LuT;Gld><B{}!uO%~6M`EMf*(X1!Y$DjXhXOK+{`tu0ovS^vpMq!jdIN!MJ+;`!uP>pXcIULu8&5-_2CE5W^glV6THxl#dgdk1ZNO}=MjPz+3}Vgo9xI!e+y^9TL{5>3BlQR?6D)qj@@WBoXwcsgy0?MR(J=z4c!cHN7td7VWAu0b?_QA6V7A}YtXk~p=;qa@OpFuEc9)7J-mw$oQrOOx6q4RbU&O6A3_hpLifRk-~(t5oI_6!pzpv3;GO7pcssq=Ne!a!ZxVu+!>e3-w~D%iu7>x+2ho-AL3kg!0^SGbpv&Rq%$r00H_7)V&#gvRz^mbv^hB()B_X&ux)W{=N1^NBD7Y!Q25t&BLD$1g;7I0b;o6rL?4i(Ru00jJ3yp*$$s>5F9ZT4sci`>l>+p7X8ybMO!8_1p*1dZ~@NV=C>)t&jcn`W1Udr4Kzrp-V;Ma*am?r>>+zafOV~LN=Ax(#c&W44~hsF7S8-5L5fNp>nz;n>G@EkZDeG5*9o%!Zl_g;SlXQ8v<*^Cz~UPHv|%VI+CB6uOsZ-qCbbK%YKMl=K72xp@6;7oWEx(Hsxyn?6MG1HDIXbLPe2^Km57CHtNIuV{^$E$WsCInAM)8OgwEOZ7u3r^+QSI9RB9*d5K$HJq~@$e{k96A*q2PdPca4PdAv#znMX)L+M5TjV<C~{3C#<BKs<d{Mv)7ND3Pa|f~<FU*)2~BdXH;JAlu?MdbDfBFb9BJqbcz_)**zp^*KP>b)Sg0Qs+7lMq2kvXfKs%l#1P?-o!Gquz(ZTSG@DQ$jhJ1bDUT6=v7u+3<gS*4M(SC4mI367W4`JST)(}rW;_(L%gXxVkt~c7pmA?=3_n|LNJw2(nC%tp(_p?4f{dLy+96fuEJs3#zr)T}CWf(dbe%y|3c07VU1`GWqEc6$!&{nX}HgJ18eq~1oLU32~Nw_Qg6#8rUDL95}e@?#k@Iz<>{1Dt2eHd;Gw?;d`t>KPn3>?F}f)fVSsT)=A$Nr`1-XkEt^tk`QNx#zj^N0J&M)n}}V@SfF`^4u~`%6(>`GWMJSh@9Is}MrK'

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
