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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_004.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_004.stl', 'source_sha256': 'd9d12f050aff204042a662792d02704053ffd5f9e25031b4dcda26ab208cf2aa', 'input_faces': 316, 'input_vertices': 208, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0820145308971405, -0.166499525308609, -0.4114678204059601], [0.31483709812164307, 0.06219339370727539, -0.29383912682533264]]}
GEOMETRY_BASE85 = 'c$}r0dr%eE9mf|HU$F@qjJ1kh9}(gs)rfB+L?aqOLJVp#K0pM)C?XgmM(eGunyAqP<z+-c1XL6eF^Ga*5GCRxR&z;{&a{qcC!J~ak4|l8(#GkY^|RaEb5Cb7?VUM(Kj*u@{p~rwvz*;~$C$|W9Rjr{p8?wQb5{OE6J5P^)BjnQl(9B7F)8!KwDc@LEx_=N54tyc?(CR2KW&}%UhuM{%*2e~iLT(u$>W2EyMmKfXROUgNL#WxV_A~$BNA3-Ch2}=N<w;)-Vb?c<oMyP(Ju^lZF2pOpRW24+}}Q~xg^Ho{(D)NF7dlUzZQLWr*wz!+BDbjix!M{;(y(t#2#<?v41{p_qE2BGlt&3QDV<y`2$_Y?Y?V!Xtm*c5{m74EPu=9!^-%o^a`b)zWan@Jhg|al;bgdX*}UU6RTA7wR~y5_wGGBrK+39_3KJios0UV75xz374YacMxOejgUWU3l3S=;7s)sCSiUrV*|*~V<$pj`H_MmmR&=2{N41W!Z{;_AX?-nUT3^eT)>rn;{O(5=cdN#4`O^5cknEkRddj|;-}2@AU-GT-G;aJrwT^C&|5oMSqvTt8sseJtRPmB;jdN5~UYP2-f0&markJnnTh}#xX}+>=T{rSUL71ZcmM_=8cTiE7;{K6+E5GSW_mAaE_mAbv`-9|L^R0_0QH|g7<?%o0eneGI*|)}T`ttoF`PO(M@{Xw1(bMs4sp@`^ee1e8xi<{|cGCf&_r81Zg~RXG?~oB+ndMdaMKhK<<F!jh{o_ym-mCIG_y2j<;UDN*F4Udi-=^~8_q93WLpM|?^W*#EUwE=oIevVf@!$UPl%o!X-ESIxyT)RrAChIv%Uv_gtMbEN$#=%zPBYdmJavm#<;U-ebH-B#S6YEr<-4~}b;hT(9#iJW_sJjNsZfp|-)H<|*PpQ0!SguV@WX%m`W4X+&yoD-@0*SO&IYg2KN#eQ_w4Cz_~A{f+LV6Es=E$<;OQpOk1zhFP30Fo{Kp-;uZ`{AX!O7B_NB@%ntIC_pMC$LD!=K=`Q5bx>Q&>nd};jJq*>=x^|5@ZKJEdfb@n>D&n>@Y%y)3SQ6F<%OyB)gf5X>mcY9U7>#HbdeBg@9#(ZDy)u!@2bDHlu{7!L3o!whA+El)$YpNqYy!kn!&RRuwo62|nai%lB-?2-|{P=Qy?N8epRO2^&pYbp5Q?INKzE6Ex_Fr(+`TfmL@+UQv8U6T&PJeo|;kzb=dR2b-fTPa%D*>fOeA8;L%J)28>5ShRT4Ka!<at%TCwjUwzSh6kh@V&LRr#J3<DBsu$_thG@qO~gJ}OX-AKz#Eu^aM~^}+Y4PvC)Ed!6H3Q|}o5<ALQ$f9uI7b^d<5SLJJqOPukoaYmiBZ`OO2{_hf<@z)m_b$0*luvg`Kk|#LhsdIdnYOl)I<_vYl&wQ&;nIGRLe?($|a{Q(*kN?hvTxEUmed@EVHOEos9i8tQf4|cHZ~4;x@8h$-nZCS_nZCS_$-en_YUPohBR)R+u$4#J_hjGPH>^C;b4T{g=Yo|-+9ze-+{di?Nc*JhoBO2c%g;60H=k?Pb)|h(_T}-&&q3Lj=PU2SvM<+Des22s@_I@8w(QIIgS>BB<B^`fKE8B+`aFMU4f(=|m)@T(UwVI*ee?a(@)xueEAzx|G~OrgMNji8{jz*#y!0L}`{sMH<$t%vc>naY-{MvI+F#?G`K9-E+1E<)y(-`JV5%~Y`JQk26I+fc$Aj-P9_f35?EB33etm_qo~AF?v-3NS_g>4FzF)|`&-&WGU&J_mJsi32d_c@InkHHoEl^8Nu>Eu>Oz|;Q{nKG;=nwkoaP+9L|L;$S9rQ7@)0-cv!G5qm+8*|YJEL9T&hS&{kKm`^r^zp_*AeXmcZ9p4UEyx<Gw9Rs)8rKF(%bWT>x=e>h4z7k_JW1>fQ9}T?rkicru~E_cpy3i9ta1cgWzCzFy{u6uQ&WG+8urt4nUuS1K^%$Ke#6xgbs!WbKM~3(UZCK#Oq57qE11?yJ&-`Sx?RnKzrE6(}VH$pmyf?dojOW)YqJEA8OWzH5fqaPtE#s%^~O@c)Z?T)>|k#4i-8Z7Wz|I=ulYbNO+XqCg|-Yn&64(6nG*WhE9UR;K`gjoP49;Vdx9+FgOH#5e|Vzpkv_?@ECM5Jeli`VP3<S(=c)krG+rh5OR&AjbQF0$Pr2#LtV#^e>`mxH6F(GMxmo^^BqmiMzaPJXyd5aIC4xuC&7h!`$TUmXo6GF18@qQO3X^mD};;DG`JWpMbqI@xE#%Z%i#)iEnESgLf65k;4|pE@EN!UeFv_AtI<rj8m>gwz?JZEbTxb&E<;zrW$+R7ZTJXWgr>r&)U${>=hGKj0DnS#^U?h_E~YQ^kc~^}3oWs6IenqWY+ONK=t&!&qA&EcjnB{*`l*d;=nJidMQzXGoyD)AwpARj;#f7cJ;Cu49IK?ZM>&3!W5=oOVU8c>SQ#}v$nk?5J3>thI9|Xp!Q%cA_tv{;1}rok7McbNT?q?a0SirmQ&?m39u%5M6TF5dcr{J%Dw^Q8(NuVW-hRef?}zizI5;0JAm$L~Er1uICGbLcF?tMM49BA<;dpo{dKz8|FGD|tm%+(sEu0K5N6*5`;Uu&QPJ$EB6L2D&fF6Yt;3eo`cnQ1+JqRy?-$D!E0_rKaL2noI7EKczh1SDS@N8mYIIjV2MCZVba5EYUH^VLHJh%nEj?Ra#!#B{m@C~>XeG_hlucB|jSK-U(>+ogRgU*I$GhYuXYEg%tvvC7`q33PfNMGnB8#mJzdd0>q^o3rt@pbw_Z`t?;eW9P*xRt)pn>M~mU+8BxzD!?elZ`#}g<iCAJ^gxWaFO+jWqpLsfrZAvLZe}!QE(KsHrIAO>-Hx625mm;GoN_DQ}q^3ZO_B!&{yDda2+w1IBzQaDtZNe6^=l!!4dFG^cFl5o`rr6&w?Y-n{Xuj8u}Uh8axASf@i?f(TnhOcp6#<*D+tgJM{Lx-Zsz#uSY+C*TY%FY~;Kh@GkV{@Gf{a>V|j2AE8^|kKk<dS8z7G58VdugLBdCa4wvOZiVyU9Q2oP4!jrr1-uvj7~Kqi4DUfV!F%8j(f8mF;hks}oJBna$3*(I3vB=2{wvRaK5pX+uKhpu$Y(mg#@o-Fq6b-D>SH4P#rIeJ%WXU3A$(1IqtX5iDo`fs'

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
