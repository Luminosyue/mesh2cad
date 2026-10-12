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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_000.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_000.stl', 'source_sha256': '8257d810d0b525bd65dae969fd911080b03eaea4667637952b5c40d732c22b90', 'input_faces': 368, 'input_vertices': 216, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09876927733421326, 0.11063432693481445, -0.04962226748466492], [0.09876322746276855, 0.15626734495162964, -0.02375091053545475]]}
GEOMETRY_BASE85 = 'c$}r032;^A6~`}&TDJ;_1uBKd8W3bR29WqfWRWd|q5)A}Bnbo|KmsUReOB2~c4SL<g=_*L1SAMTcnOGLMOj=%r=3Qf>5Oe>>@ux7?Kr*X-rsk<@8mk;w9K42|Nrm1?|k>2``z!p+#zjrlcp^#_g@F=spKvD;<lBz&1z{a%FbVqJ3YIgSKhqEjjU!4mwzU288>Nc+T=#oB5P?<R(8Sk{G>slqz7_Rl6r=ca^~hQ$j{81Ha9;jTlnzI*#+4)FPND*FWdIr`t?oj8S3A?XJ~oofBbigeG1XPjXZf)@~DgP2kji&c5&ZXKkxXR%d@^L@pJ2=F||R*Tc_taJUphpIHAt+jSi1jpWc<g&s}rtL?;v_)Tzp-6JDRzuP}&P|8Bigd~9RWV-CNo&pF}I{U?hPc*+Ea$2re%?|)P|^@^vs=lRVchsRFTINVBp#^Kf%%Zh_|eAUM>@$uE0-8$V0o%-P;CrT1{>Xn3ftx#{bPPbj|ykoDI1o6;_+xI%3zdq-P!w-Jq_UH1L(jacmU-QVIJDh&TR!yvQc&|2f{&^d4=8gS+;9>W?MmjuX`k;6{eF%SbrNWuN#T17}IG_6JHtzT9{8_@f^7tn$+&<Gc%_ILhy4TO6DSc~$>O?<#+~Luctx5uU@#0tl|I;3~&pA);PMG(f=iPpeyHFa$ty9|y6FBQI{%lTJAlKg)9-1*}Pr~`k`HR~(HLu|zHE*<ihP$rx_l3vw_w61{T>o=EEeh(V$5lTYaOxYb`=+_+o5xk(G&lY6=2iXCJf!OD{%9Uk=db${3-{XYoX^!G3G3GI=<F{Y9^P_SX%LV1{<<ikPP3QX{*<jK58{!VTJ1{UW`Aon^R*xz>z2MFVcx&?aQ8h`-|)Duzx9H9ygGlw!+jFZKf1{}@7(XE4{uMsR1?%6c!T~Z?)Asi(fv`}>yP2OKZ<+(G4tyFC?41Kb$=B1`eW*-{?s48fBS<0{V`nkM|0C3ua4@E=B7U$SN+l4^v9c5^+)r#uCMx|x#^ErN3WmHzbJCJ+J8K*_MZlv``2*2|7dRZACIg3M{~3Pc=M|LNAr-XulFC#W9t0%{!{<w)+NsQ=;x;4`njpN_uPaxcy1c5pPQPS=ZN7vH^bljp)81d&r@?g`gy9j_dGS6{zu;_Ef3<}b5?WRAN`zFJXZU`&V=*V&tJtu`aGX&c`m3AhDTH%8a%HRkLf=Dz<SWXGc}Lv>#lx(#z)O}&ogU6jq|<uofb;@)aB3L>+t%|-QRnf$IS1&nctQ=eE0ijoXqb@&Evz}-;?z#UnqC@wls%F_#LZx{XqBkYJK~r2OPfP>S=#{&12LLefQykp!>z+>VDDO+%FzK)}uD4PV~$~cRg?JSQ5nRcjUzqxVm37H}{J-Z@)Ts-t6C%2Jz6k+`<H|?ibCi4a>@ccsQl|o*-`S3-3JpeC6I>>U<0j>+@0fh2|0UeWN8$x?J}YZtYb4tXz?>o;|Ma3(e!|`s({4GQQJ6XTF04&bo@T{xy%X{-deuUA{WqU7zOf$4*x&oa6N0LFxag2wI;W*ZaBR-hOVlTAzmN^{Kg8pB~ryx#He_Zst|%Q**OEJ+Ak2#m)NE+^kQ{y?xu9r&^zyhxPgBeOvK}`o4O7YHrr2$JP4uxZbxFkE`q3VBc;r@USzV`g>e+^Y^&*a7LxW)!+LKIDhY3d2^1q>pby2gXZQvgXZQvLwI@LDu=808=8CXH~zS_D(JrOxVkSiH}{3%dOd4y*0WbftxwI(dh@tiKbl8WeSO_EkL&YS*FBtG<JMR2qcr#4M_u~6TSvXuveu70>2US_&Ex9*o8kKXo952@x3q+}pYywP_&VO)p2Cist(I0!rvKGvbN4WlgI|5-4){^8KKm!9{J*b0tL$?)F3XF241F0d<G;m=USP)@JGK#`H`uWiFM1PRbOrS`k+-6&@D<b-e~_qxUt;Va^US2?2J~8LZ9rGxUnVxeUt>&IDfM0>SD-K9W&CY?Df8q|XDxa)wbr87;YF8GZyot%bSb`!`r?a;Qutep6*JEaYOY4Fq1I}28Gb#n4qncfuoCK(lgrR=;br^+zJz&ZQ)dnO6>6<Pm*Y1Q>*0qO6Lx@lhsfpV3wRm7h(EwQ^QiL*dNZ|NK_9|zAvVG*854GxdX?lu=!<w6e+Pe<d7h=tX7mnfZAMq(w-a07M;R0LI`xi{E79-ZW&B<I>&&x^Iy=yX)Y^eQir+<ShgUNu>?HN7$w$%e;${3j{7L5d6?F>Hd#P23uEy^ncER6ZOxT;$dxKn!eh)9>SMYB#&vNSQMHf+PFM2n=h+2DKC-9<AQSSu#4fGYfjK7aR#XQeZvk1MDT1Dtr@uH7W?^W_{^eOx?>We>4oPu9wOxPkj3Ybsw0-v6XmpsR(pTSF>>C?G*$vHkf3om(wPv_w!&-Us0c**m8dLdr&vp&5TFL{|yFU2qAx*EL%zl6RUy$HXE9*7=o$5=Zilf^%TmK^qtWe}pr5Mwze%<%)@;#0}O`uTi6LU>m~bT{&S=x*rl)P4{@0Dm7Lyg#}>$4l;OM-qAn-i#&jxgmJbqwtbPpogFbqX$z**dzGC=z(a-y*X~MPfPAXmSgTkOYZ0!>qrO>k$a#+=wHC^$4gE|OWeaTJ>d6n%uu}KVd!LZ3Oa@3Q{cnVgY4)@PJx@_diutC!Ns>F3v1`|?Fiu=h(307hV_AUM$3BXiZ|;=cq;h;bSnB$@<_DgU!osHKSqwAA45M)h?ad~5x#&BK9_jPa`%P^+OTvxrcys07QsJ7Oy#pOo`#=_o`RN~%W+fDx$s%U6PCNLOhFs=Bs>p2pF9mcAH9&AiC&0aOiZ`jeI*kuY?2+1<1_Ko3E|o3Y(6V&GCmufg_gX8<Fe6N^xf=RS-$I%!L`alKaC&5waq|3h8La6oEdyh&UX~&B{7=uQD|WkIZnRc2*xJCN1z`;3!8v9dLn(DhL$=HbBv6S#~VF?>+>X9J~xzOWPBX?3G`5(AJ6B~7@L9~h9Ac9W^5dvdxZJ}3DNhHhoXn`d8wC<Pa}&TNr;y9J%}-358y@jLJRAI7cKjg>=$i02boj$Hrb<P-|WIQk^aj*{SaRCc{^6wag7lD8#}J!MeoClj@fY)b`>uA9A3ub_?5&t_)Cll`?Vc4uo}4N(|8$=;zjRA3p;~<p4bn6fiYn(+Hn?k7B0FDFXJolFVcrP*ebl}PL}%|?M@comELxOcR>s5h!z$?cjOv%g0)2pYljxr0WGXEx&!ldg0--tnH_hM#ouPft>`=KxCMPHUUYLpbW1|?&j``23DK?WxC?zJbF`p#E3}N~Ti@?7OYpJ}6`+OBMGJcdEi4x;Y!+Hr9$MIZw6KL}VT;iVnJ*t!%eA{kuI0Mcq0bVc&k&;b6QWNOqH74zaYFPtLiANa^mU?^bGX5drgq#&z6ssLjz)GgCR^y6?f9u3KOx_azT0xwMSF4wbQ{ZEJ9m@Yp?_|<>#Gg9E&5|SKCt5>@`vcO(Ty6nZ1O|@_3itAQRig+{}E1qGV!&M|C8U@2YD}%(njBKqx+>BI~Vj@S>@J$0X{VKSO'

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
