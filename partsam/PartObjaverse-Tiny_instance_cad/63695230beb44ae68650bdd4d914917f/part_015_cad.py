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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_015.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_015.stl', 'source_sha256': '3b4f03c4bd8e7afef8d151fae8ede2fb56ff481b978ed33c6edad55a7a8769e2', 'input_faces': 158, 'input_vertices': 105, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14747431874275208, 0.3242344260215759, -0.013883110135793686], [0.028570204973220825, 0.47596555948257446, 0.11049224436283112]]}
GEOMETRY_BASE85 = 'c$}q}3shBQ7RNsxA`~x014qe&ikGLnyhs9aP*h$LzVSg^z>AOND1w4DHJ(UvEUZS<QPI3k**F>5Lq#Csm?bT8T%)PzSTnb5mS`Ho=%|fYbH2U*c4bzx)~q_Nz5c)RXP^DO4@YvdTwDhTzJkOT1=r8zJs^Y(PccALSj$!}F1D7BT2}hFlkg>9UiY*%XXcdLIZmQN{K~YzT3%dc8mpL+N)k*Fim7CI*~+rQWd+O27FeY}sc>nz)$q#~6_#3!`;eGubA%EX8lgO;{KQN4LM^p_&?@_4-hC#;5KHHk!&3FWpOddQN0V<~y|an*N(cL?`e}KuCS<%PRcYA9{=>H^U+uZtK&scWA6`Jd@LEcB6q|+p;4JcOD?5ApPW#ALO1C%CbKgxPU#rVGEAKVmu0zz%?lAJzaE1LEx5M1dAkKf(o&CrS<SXBLaehP>)z|NOQhm#Y&yG;LdJFq=y2;n}wzGfp_f*GTbK@Z8yS1?IUCe&<>oi`ab}#v2e?M;b>j0{w2V2NjuUW_!4Vm1Z5gA<PRw(-`f*N_gQ@PIHZ<4RhynTT3H$`!sN#5+gRzdk{Wf=L|(Koo=swb&Gy0?k_HRstMzJ%w^KZxt-$H>=bJV5#Oli%pnZe<DkFVypX=xAa;_Cs#B?l|RZ5%02pHoAlI{#-%*w3+M4*IfL_S1-CyyV{;w_IK8E{R#0@-+o~^*ZF5Y`zQQ(UCNh|uZ|r<bu1-Tnt$Eb%yqW6^_ow$DVX!ymQcR^V)whGzwBzI`mXcX58O<3)QuhFtAF77_Sp$EE}O^h*8Atpe!Yt7TPo&ooo#P%yVvjVI$E#3PwP0gf_%j<iu!Mxdx3oI<!Y)g)*PgEl{2Tv7sW%!w^<Uo&R1JG|BQ{->--4b5B4SOFMW;jwZY%eJZn>ildmRiVgI8_USHp@Tgb0>Az$h95AOf`%j|!j&;2>(%kviY0sEVuXaD^34gB+R^7V5kcwHWg<o#B&n0&4H4Q}_H9&WeVi+piyG4F?|tEj&1;D-0e&v)ngucY(&a;hO;z4|5lyE^%Njenf|)#G^ov_*5fzSGFpMy_N(?<CdNu4i-oH!tvbTfBH3SD859a*XrwUJ~l5W<KxU+-_VE_s4vMd~N@3p8u#i-sh&OX5OD~@_3(Y<o8UJmHoA6d(Dp}KAr1Ve$V@M*VFtybPeMCRleNr+w1uKklo!x<K63Xj@J8d9_P1pvVY|n?tkS|T;Kg{)BW}Dog*#dDET7c3(o(zf!F;n#azcZjq`^za-F7V&R@gxub1-sM;!aOk?KeK@OT?8^8Ea1ANg9`S6m<OA7R}~zVPF9w-3G4%h%sJ!t*feD390WH(cl2-*TPPo!p=7Jo43(Ni+{?;&Gnmo9Uc??QK3Uct7hCdk&KyI+y$3)Q^6Th|pW)t7#rwC;lbw|2qfB7dtNTxF+9a|Hu=ZAK%V(GQ+vf6ER$W;~viU7)QQ#BZTv}4CeZKy14(boeflfq?vp@$IkoqWE=Tv?q#m;$-f6}i#{Y@Kj=pJ+P2x;ZrAi)`C|T7@+|?Y4^h5XB-d}h#rcIHrPNMB#b4?E{iOBO56j$gx}TgxzSg>|hWxFcR#N^WcR#0}zxv&C<Tur?rn<@FIp3*u9gW|wuA1_y26FxET?;9{W#6+@C##$5e3DW@erFf?qWMMkU%&Hf^7ogn=W}v^{o;$9|K;Tk)Lx^`{_W?|NTc0fBpuYw{@UX!NS*JzMC}f*WnbG~Li)#98_7R0jr|32vq)zwtR+9Rfc*>CcwXvXC0{&SMZUVeXdU$<En*AZn^VZwIxf+8v{A48j{2|t>oa=p(y+Cxr^r`#gmax8JE<R{p==vH7yWO_w@=u(neM}tI@0z{<g3pVY@+<0k>u+=&E)I54{hanShj=iKYf9GC3lUD*CTZ&`PDI;|F_teQ*wKKmEIVWf4Z};u_8uz7+<9&h4+1uN|Tlg`s1IZi%0)|pQPr5pZiG~Z}cJ6hy)`tjYu;h3pyE`1)c~^15bdaAS5S2)4-#Q2s0vB&LK1$8U_wSUN}PXXoTc3&{%L1GzJ<AjzwM!LUJfH7#s>71`Pra0|!Eb!T0(d2=xa`{RKD>{1DV1EY%0>3-yNjfMv-47q}rLdqBOx-pH5i4)ucifPK)O7t{~z1s(|X2m50@k_SKsK^5>2=uoHv9sv!3Dqscc7Xpn0hk)at;oxwrvE)af$<Wc@(OBbT=s0jPScQ%O-`gK5Gz~0uJXi&1K-0idGr?1!xzJ3o)GV;nN5Q$^sn9I&RB$$QA~+kIE*xhm9hw482d5$=Cm<w`MMyS7lfY7Az-Dk1LUIH&6fAWZI08HpA$d4L@?dBnSn5OI!QlSFvG4msy}|v#4?^9*4}$wZUBS*!C#Wmf6?skw$pY#j9G7Gl;W$4oP%p3xxG!`dxG&gKIL?VDbP(7R+z%l+Kse4%0CXrg0Q@jQvPn43l?fUGHi4s|ao}ihqHvs_L})TN5j+X1f~97FCxLT>W8ddMbHO>_Y0#<Qc}C<Lk%y2x7a{pEXaRVU5mqA>LQB94!3&^Pu+$=OF|-g`1TI4DLTCZF0Bsi{BwG-Y=R@a#=V1)<5t3&kBu|IV0#66efaZboFn-B1p>yQCWjQ$yaQR<<x^i5a+{nHDkoDhB_Wr!M|H&;ztsg!%a<lr-d2lxVtuVAvo;vX#Jj>SD'

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
