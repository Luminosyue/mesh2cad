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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abdad363791d456786cdb511082d9d63/part_006.stl', 'relative_path': 'abdad363791d456786cdb511082d9d63/part_006.stl', 'source_sha256': '7932e81bce379c3f10f536e80e12864afc8f30a6ca2035a70d58a3d558b2d021', 'input_faces': 192, 'input_vertices': 136, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-4.016136646270752, 1.899682879447937, -1.4106429815292358], [2.8588345050811768, 9.166264533996582, 1.8223203420639038]]}
GEOMETRY_BASE85 = 'c$}q}TWl3o6o#i43dI727HYYk7D|DZODR-ZupE@D<x;^42-;S9N`XS5g=%dnhfCqXgg}gmzM(Nb8GJGE!RYCm#290I5J-sW0|8?~3{ZH3xL40N!#-;^iP4k%`Tzd2_S$=|wP!NZ`nrtFd@uPc^8Wf__RrCAo+rrh^1bd@=kWvkVqJ@l9PLT-az}jm`TWt=hAs8G)4Xo4x3neJwXd_ZCQ`bpbwz1;q_nl8^LS_Tk;abBmYDeKo7=l$#_wutJ{mKB&#S1cDvwmoFOQsz{Kwx|vxLa`+}uIK@ver^QNx4P$L_DT{l;rK;x|>#dt&=T<8MtA-)r6fd&2h5eVjkye|r3e#K(v4X1nqSzRK_WI)C7+{8#SY8!i4|?eNr*{G+blPq_S>{ciuO_ycF2>o-#TNX6A@;t&1u!*IgkH+?qv$c~Q>f9H(%eZ8K*SL^Y8oj>~Hts+-`-`DvAU*-3GoqzD&?W8~9YN~(nPIBIBpQp_0J*p{o)j#mndIDdqC-A9%Q}sZy4tEpDzI?y%LBi#eKjf2N`_W5_AKJcm_LF44$}T-hIQ*ukmmjC(@%yXdgMO*_pkFFJsK1II`t46=yzlGyE0Km`SA7Cs)hF;(eSF`q&(N8iEPG#mo{&!--`D3b<ook}+mh+*m-2&t;fMO-$Lspzhw6+UswaM^KFSZ)bGb2f{eJzm@7Etcbl&`UeXj6B=LbJ@PVhtLLHmARzFhlogbQO&N1nfJ4S&1*=!cJ!=K+7P#hVg!#QVM<KUh`rlPkaWb-d26eLueG=9XVqJMwE^$Lsvs58}J?hMoD9uj51cl^?`ktj~z5bK>+(A8p@0KPmCn`LTWb{Mf#Ier(@9Cr;mA&o>Pz>y-N<;qc`?vVHshO^LVeU)#6uU)#6uU)#6uQ<v|rXXw<EOnctv`qaVq?dMp+<@<H3>dtc3NBKd0wEvtuLH+SV^;CY)Uq6qov+{L(sQ${=@u9vbU&n{~rF>nV(D~Fp^|^BUj}hN~uS>Xm@`rr#hkWy%WBc}dV8Y?cdzu|@zt<%kzFv<$huYWq?f1Hb!`J!sxz)bTZ@(X=)XjQ7wBzmfx`fMD>#^S(oq44G^(kLp55B%|C!TFeVvudVzFM2DPcJd$=d=6M>%g*q_vux=^#6W(rJFTm8Dtuy!}1%2&O!^1=31IT20DXrn+&!XY(opz8N6n&)nGGPcq6f!xwZw~#<fk1-Du@lW3bL(16uf1gI5gJ8>~eOM~Pj_wRP|YuB~Bg)XFi{Kw3E2V4^{;fqa)vFc|MiBRwzApwM8F!GOUjgMNb#40;Vt81xyOH0YKd8=N;dZLpa9d1&E9Adh(#!R5qC+(Pt1)>KZ6uXDL3>zZ#c4=wy6ULpIN4=(_sr=f+*7$alnqJ<0C^BjX>bTM_A!`}ty0>+e)a|&9xlrb_kf)>u9?j^)bhNs~9Jt=`_1JUEq!bRkgoYT?5W9Z)ugPG`=^mhh-k3o-NOc6O>Knu@e%uGwq;@T?qKNl_hvcYQVz5p#;Ww4w*mY{`~dC9YoPjB*I>0dSLn~oM<LG26a)g-upIc2_DbS-_YVhv?z;g^_aGBuwHPh+o33@XqS>^YD5#-oKNPy^ZjO7u$ly^KB1MhjOmr|dTuol9S{$(e)Bp*O|ktU=e%?@DqOp@o-{Yb-sQ2#;f}+1|5zd@OU%puS7cOW5~Z>Q{@drN7ImUm3cLzD{RdHRu}pRl&N7&_&eqT`&1OiKB)00nvSE;bvkbt_dyN%e6jB_i|01L!Aa)XyFTZ^7jB*_!tm<4lR6?F*3FTEqvBXKI0A>96}49#5+yQVYq`_lJg8&_y}WU>;bfJkC%MTwiDA2pTYB=!R_!tAo_i@a2vTK=YF*CdtUN+-D(g+3!lL2CZ-kMPcF%M94*|!n3$zoxb_D7??4MT7`#c{kD-Md4c=yt?P%e>Uh*uQqBn6^`d82T_M?Sgr}pRR)oJ)FbIN=>(L3pDBWpN{7Ji3$`l<N<e2%^DHrR#U#h&BLcM>h!M-62EJJ37m_g?mR5G}liIc2}S=wABTP0k*454|}=&h6;!^m`9E+t9*qNv-PA((^N(_pkG3zqq{gr2HdYk4$~-vq$!uT)|6VecdQ|mohI+=_7@%mZ!D%4`}lM;Q'

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
