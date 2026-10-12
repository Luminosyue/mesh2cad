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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_005.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_005.stl', 'source_sha256': '77563fecc7554ddac5c29a8023aa3532a5fe5b48ca282453f3010f7c30cb8f44', 'input_faces': 160, 'input_vertices': 123, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.04006216675043106, -0.04246076941490173, 0.09380310773849487], [0.19172614812850952, 0.3320962190628052, 0.19893373548984528]]}
GEOMETRY_BASE85 = 'c$}q}dr%cs9LJAbke3=1z7Tam<f0M}QSw2xq9S?)DSTUck%uCp1iqPSO{+;8|47rZ5U+-lSyWmYipo}6>Xen>^wR0}9H*SAu|FCst3AKpcW=AvZKkO^bLRWm&z}A5*|U50aw+z>LgNH~5=GN;cTGe$A!O?&;>4<ox)oJr74_-MYS(rVG34dP%&kQ;3XA7-5vxRlyS$>ltj;|~apzW!a;GWo%H?${>PnX_SYB6NA$@-7()tR+*Do%utuVGzvxaA<DcM8Pln0gn_=z%xpoVW~zFUqZFXIB`=_7B-RBv40CsQvdB=6tQqdl1SJ^Ah1bllwT&&$+0U-`&dN1wKFKOOh^`|LMz9j7<z=mp6KsLnHcslIw?Zd)+#^|qg;dS9-6iTZ8nV;}z$2g!>MlDI$W+~iS5o3^Qi&Xbys>rK*wd40+h8mD${;>%R$lasdV)jTDyP}X&RWUJ%wfjWBPt28dpL0cVhIg7mhLSlzZrT<s0Rxb{)_qYG{4%L~T&vja=c^<-co(SfZslHQ`XB)|Dv8U<0-pYJEm{%94&^XnSw1ZUlmsqZY`Zsyh_jX-PUd!eCWscwUI=s+%{Q9)t+4sJ|<M}w@WKcg~0gr#><A><@?eB8^$Pe3sdF|0h>HhkwYF?u{U)0$8JAI)4{x8UjA+0peqQTW_^(wqSruto5|Ht7^@qP5~jDDT^Un}PNiyDpx^Zxh@I<GQ0<uLiSQMU7%UV{&u_lZpMV%7-q-XGH2f_Z)RMZT_wdL5zqzRxb$`a8TI{gpjy$cqnO<MID^r7f5@pIfK*&s@Xj{b9=+{M;9H(tbP-rWYRe=JV`t`jq=0^>x_pm&1E;zkCTNsh;MVWb5zrW`Ct;CwcwSdE5Fjy|{edw!VB>-*Erv-W}Ha==3`7qxW$9G3qC7aGg+IFHSGa^>TX)dA0R@ng<2%E2mfSzVbEvOkRAqgzBhRFE@Ft7jO2TeBP^jZRb_4KFjadjbo_3j`x+*`|!T<&%D-Vy<g@yo!%U$cTh6TlQyup)4DE{kdoup@u=qe$Ke&cfBgRS<n>yAhjl#Ob8nLuQG+h>`1$+A={0=6DADJ+{-Gnbb?Tk?FuyNj#$B}epCf2q)yC&KZS@`AtnXcRiv7elZP%;$I^Ux4oK&~9OMj$<o+~x{SN6lVKV|bLqWF9D>fooP*EcDrgL&oa$LKwvCTFrQZ`f+<@9=^C1NX82e*X?SZ@<lF$Uk<D{lY(<w)yWi)AJ&>*FH=27mhwl^U>!J`<L5yTD`g>mcO45P1<F>F0CzreclT4YWKLH-oNcBo`)Ax*@wCsZS(U%Hv4TEjn+C&Z`RRHjb(rBI@dpVhP-GlVL#z;qt)vhs@WH{H&OldSK04)guQRwF00o*Yh-`s@@|^v7gn9+aW}KSbb!2`d!5hQr;UAjWs}vb<KAMgW;a>usI8x~AL;Sg&imdq_Q&tpZS$+6`8;2>_^j8ZZBAmpIoj^04r71pC!g)UIDB9}YjfC#gzvH47jGW>vLag@rw`QGSjhgxa-X%1aJ6u@r0%snZ&erAk1pP0_2S%CdalLv$Y$$vtNnhI{VgM&vwD44I;H5Cvd_9+oIbE#=1*t8Wo5H%eL1|@Ura7%UwvYq?fGxm#D4IV=72A@{fhV|Wy=*2VW80>jb9O!rIw!%v_ptM2LB0BHR9j>gviPKzds@FFvgH(v}`oVLy^hgq2PhYe&B)N-pHQd-rycan`AUOU-@W~??R3M-vu6p90nc*PDd)>bnswgAMjvs0`eAc0=O5lJGd7(2H6AL1LK!mC?5r*jYsB!$Afc_ncy6-8<_-lgX596g5$wa$Z&8JI1CvA4g<T80_*~ZBD;V?!I2ohydDp-2<!nDAg6*0z+;hl;IZHg<VbJ^I1!lwP6Wpy`+{S^U6GOCNQ_x>1g<R_84B)(xrjizz){#22M)vb0L*n9G73Bd_htYx9y}cPatP859wYeP4@c&J3$bq;cs#ZzU{1#&3&ASpbON#nJQ{PVBBz40FsGxDdEivcX%=!MxIgAJ6`2CQ4fER{*%us&ebL}ZY|C|UyWq7D12)%=WOIE<HrJqJbDc^y*Ro`Dy-POV36iIvNuG!%`A#&+cc4j5LzA40Cb=K7Cs;m5@-qk-0+tyLmU$~!W)fItCRk=JSmtD~Ob=LQ0a)f(u*?jw%tWxvSg_2l;I0_A<Qk)`G}>BlHMUn9ZJE*5A#1@)(RUTN2HWe<XAN>WxC(vi!Ar3%_pd-7$xE>PfYBDA{~{bykA1RF9da?a9LJP_7h$^&eJYU^;8{j1MgLM9Q-=Ms(MR$^Y|k*-0vxvh$IQb1ndl?gi|u=jHV?<m!!a|kPxhIPoDZIZW2S-UVO#DmMjy%dVS6t6-UFV4ZMnY$eI(y+ZhN|f#JT?IUyy%)G<uM&|B!SZY5%jsdSt#)DDX!}u_sJEU&aCmp&PNDD*Oc-6F0m'

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
