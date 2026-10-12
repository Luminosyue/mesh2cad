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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_011.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_011.stl', 'source_sha256': '934dc6fcee3d195b8401fb94a99fe1226233be1fe87cf1262217da3213eaf6b5', 'input_faces': 120, 'input_vertices': 91, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08674730360507965, -0.08196227252483368, -0.32650864124298096], [0.13736172020435333, 0.16765260696411133, -0.23459482192993164]]}
GEOMETRY_BASE85 = 'c$}q|2}~7d5XV0d3Op}F@Mx<p9y~yxAfTcYRzXA&1mzIY=%a#B)1rd+(QXmNqh9rDg9oCvv2u!{)-*h;QmqIcn5a#Ym#87Nwx-pjNoktyH}ik(Zqp`B`^aSe^V`|^X6M_tZ%I$-=H@H-<1Zd9`e~b|mk`o=2w$<huz2Z$xrHTRMT=Lt2yf!@<Mg}JvQpD?UBq&+##&HVGPl?|PO-+$8*2?wtn(HXFD=e5nzN|5piuIp{I^O9bzU+*e{rE62gXE%D3L)S$~xu0ek^(ms!w!Nv+k8R^_28>|Mj<|SDPb=Yejj)wa)f-I_~!P48`_7jpWx{B(5#_lKIxm2J$OhZb~msFJ!)BWj&ogE|2TyF?ZC)oTlRmA5$IS%G|zCqkPS!AJx&0Eg-ILwQ&BJYN{jh8#yk}$cq7|xzGCT6gw^sr#fm&5cjik1NCip4?jWt>Y+PyzB_Z(Wn~@tsS`MVdl~b!d#lNJeZcv%nA=x(@%nLBc@7cGZCyAoZS8I1RqH9PJa>)q)#%T84u_a)my2m#aXgv0{kKx$;%*|((;CL>Ry?8oumwLqO2>O2X1>3L_i2}fuXo>M?mw}KdCI3epJh*}Pu1&igK?f}$4Q>&=0n6Q??f>7@a8%P4>p+gu_~AQEC3(dL0oKeqkcp-bLX73OGU)hc;@0l2+uR;P43^5xns^Zd>_uX(cHwQ1H^5u>v&zC8Qjm$(|Fy{6Ztw8PGKI;^HRTk`!K~S=9Bn3uY2IkalT);A5k97*ISyv`_Riub?mKtJz7K-_v0JK^-nT)eqXfjOK-6s!2O+QtfKWZxW27zNDZC0)3t(*2XH@*2cJ~)d?p<s{~6}vUa>P?o_G7&W$D%VtC`0gB`%IFyF&cIa^m*&%^y;J!aT~??)Gk@{8N{R3qK#q7f~L>Z5^#AW$Y*)d5Q81`cwao@HXasOPh$7oTuxpe8F5B*z+9u&EA~9;5Kn(|7KcOB-e8OstyxZ->YWc=2lJdniQ&Ue}0wu7I)&}*K*3YkK9Mx<~NAAcH@2K+uJ#R_i*A$lqdBs#&;2S1dkwYvj$Rqwc<AC|G->?Hl8Kk5JdeekpY~)X%+Wbww3GLuoACSQ>ngsAd2#BQ9-7DRR0djSCU7Y`WFq{f90lfGjC$<II)d+OBr9+lihs1JHF!U%HPQQxDs=?{*e2eza6}j>(8*%nE3VYnEUi3Zoe>>`nQKAasPwEYmD{PchF}J_}Qi0&%|=>bN@|KzIJ&p_jCW5X<hq%Ue^)ZWzOG%`pde^_0zb%Eqhq4u}|$??z6Hkpw?9XYp$=f%&s-ox3_XX%9Vq)#(4_M9_CL^nDSL0^fS20#KkVu>3m#k+TVfqIDfrIo#{R);`>BVyy}eiiMEmNlgbU2I#ZqQe4jWT2GyDRzsKu3lHaH^eqXe*dR{lf%++6NF#p+g#_zBC5r2QhKA(E(6VDBM89z7dNBR<XJ~u=Zo*S#$PEnnNp2RhO3qLnjv=di~^LaiOyoo!W?Yv0W+d1hA?(=a6_4#5KapnAv%(X|%d+Z@@yA{fOOEF(ppS{E#Rri^1TynEH-SieU)GOXoc}Xv+o0t9;H80=r3MHZZIQ`$hLM@2;SFcbJqr(5^JCtRF-or562E&Hy=43;3^MMUEuz~V6h4~oR%R;_3vRMplfNp(YJq+v>-Fm_L7?_`Ky<xq;`swD2V}8)R;d??$?`b$!Y7cmKXz5*{rFVh$fEMuGpryxFk#{p_FT~P!hjxSZhVKh4{j1Q@_c!Q4i2Fkih4+V+UV$D8?FZivIzTt8Zke!|U|G85={5_N2_}!{=#~r12FpZV4$R4N5$D0rg3d#|Y*?;=1%XK)2yI2237-WWfE+7)kU>w!xzcAqOFk7$>M4k&o{U)P1jJHLKrD4UVyVX?mO2Kp)MF7#9gbM)FvL=aA`Zl?Lg6C}dJJNzV-ZXJI%26OB9=M{vD7JurA|XU6EjGIPdDfc#DSQpv&JOUkvbJ|3eHQ#dU5DsB96yFCn1){Mx*D^xQ<xxIIv)Fr;b1zjCn+0j?tK{^y8q%Vy==UW8V_t6QC2YZ;9}#LB}JG#~!Ni;|w|mv8+D@wWkTbcaq_!KubOyO!htsdp!z$I(0PSP+aFI>_IB#EA<S->DVI~zouK1ZjsO-h@~EhI6cM1)wkO}{fqwRN27<A@gMfTo@xGBGM<^FhkyJ?rKh;l^UhWOTcZ0T@<}Rw2eTP-ss'

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
