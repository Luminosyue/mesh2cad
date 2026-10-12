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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_014.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_014.stl', 'source_sha256': '1a32f14ab0be7ed1369ac3192017f6f4a79e7457b74b255eff421f8ded0f4593', 'input_faces': 140, 'input_vertices': 134, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10390528291463852, -0.1174788847565651, 0.46075183153152466], [0.11687184870243073, 0.1312909871339798, 0.4997556209564209]]}
GEOMETRY_BASE85 = 'c$}q}eQ;FO8HaBYL--0LBtYyMxzR|71WZWMBqTH|id56YZ4hb%;V#Lh5D5vJ4<aAoLSWSK4~Jn!al~O|3Id8{1QI}^cPQi3S{z5GosKohI+kf^EmZ6#u?gFr^S-|u_pFzhPP;Sj{GR*d?78Qjd+x`^QxSJts>YuT?OXrEuagorP1a;BRcrV8Ti4h6TIO$TemX`=A}>F7?yFi}>8Xj)+O@4&b-tEbf7U`htE|2_D@V_&Z}PYLy&Kmw`RjbrKjhue;uF4QowwO1w&&#K7v$*q**W@l{eS#S6hkncd-?o(BK75S&d4-JW)76gu{~SJ{-e>;?5EtqtL?R86Hmzuj7(?$Oz0f7D_BO}7)ez9>Z()R&kXYBp1tJVrC)SYyWz5anfjjX-2Uc@*C@k(q4s)L=&anfJ}jg5?%@ZheQ?(m^6rHf0^I&j)IMl>*}JRWqwUbqKAFajn?1bWlnZj(8thZN*>TCD{zJRTYdfxxw*u|QD8pY-|5oQ^_BAz>!ElI=tFxE3wc$zdU){oUd#&?T_R}+uMvmXwn#kjfNqw8!e@))l8tSI@wO;Z8%ulqp+Xps(OXoX~mhvw9>xwrQPa&`UdxXc?wu!v;%R@ahZ$k@co{csi``+s~U!~-&M&Bu3R~@}PKQ{&<y)|0b%ljSXae7Nm(s7;pocgzhGW!*e^I{JEu21n}=kayL+vm#&Jp*4z-ufh-_aDAG;N-{V)0@Zs{cIfXJQ|PNn@v90{muoRpMMP~{tNvC_kWGgqc@$rw&|=g|C;x99_NXgv)s=huTNvT(!br0?E`HIyxzlqcl6QySU1nV!R@c`I8S_boZ21Osf^Ql^CJ0RkLyjP{jtwzee2fY)9nB1=!4;J_<B4N>*%!u4M)f?z1|Z!{%CKH-`v0DFl{%)ouzd-l+hpQ&Ezy?J=oq}4_4@~;>|DL$9m|3_mj6ad$8W_<@39LEqVR;AC&pAz1zP{nIGfD8^56AJX)sAzgGX;Zfak0$k7`cF84Tj^Wbnd&s!+UUpvG8pQ=wgr_M8cU{q7qbFizro#*+FN<X?;-A3CP3CjJ)=$O_*{p>xXjNkUr*Nfg*-Aw(L>{t4+KFMsNdDt@UOyoENH*#*gEBj5or1Wq5V9J5hPVJ-jYkTvhI^}$g`8DI|eCgqfiZ@P$mFr@x{gHLJ-n07^zu$#*s4L$3^BuGf-GjgBQ;w_QVXVVf6(6Yj0MC(a{2Y1Z>Nwh8MzS&wdfMlWG~b>{%Dfq~RyCD7%(FRjzQ5ezeA)hc^LE!;t>q5q-JJba8;xtz@0E38=DoD5++kgrc|GLaQ(ss2Yx@^}-Q(nqZ>}lp-1g=NSEKgJ-nw*ASr5U<s}EEExE}5E8}04$8=PEE{(IMTVmr70xK_On*#6=S<^E$Nc9J)HGjRX8+!yKX^BxEtRJ?iaL)?El$?L9}C#n7MOK(Ju-}ce>ZNrsCKKl6*aOIOXXDy=fyN4$BJ9+#06>t@?PyUDUoE`HxE@SYwyl!2kCnJx`3caTI?~ZF1`}`()53s8J*l#Ys4-}4&4`hC%tbe_zg2%CMHtjbs_$mA1eLYV5br&CGAN5|Omwd_nM7@u>ORjVKRfl;0Luvg^-hOW}OGemNE$1B0=kYIIbDsXb)9jAC4@7(W{nL2xQ}Wh*IqLgZlpni)E*WBv_YM2K*S%zfy!{@lg{=W6KlXmO#Ptr1=S2G3?ECpTTKWR}==bN!slC*X^$NeAk5=<IEAJ+6bv@F}zEbh-l4iWet>o*gvXuSYB5EHPUBT@=1LTbu58WSvBiTHD&)=}$y*v-YYx~PR%C9N?`ClzcN)W%6L`@LCrs}<sKcy15nVrr*rPdexcR!^Ha{u3-Qa&+;hebUps!P;vQM*KSBKIJ7gP)e?K-3nrmw(%dG{KWZrHhik(<USDM5cr91Q#Il!3E$)kyYSF!F9-5a2>c2xdGe=ZbC`kB&r$t6mkRjDezikEqE=s5?KYV1TR45gBO7BK&FG!F)xxI7ga548PWq@23~@ad_VF5@crNtl;nj-H+Uhq6j=@~1(zWo1ebvqp(OtZC3!LOA@E}GQk3M!kUs@K2L2gJ@+#yC@G9_1<Z|#z@Ds>t@Dtz~<m2FZqI6L?D9N*ssbHBY;9Pv?K4cC!M$~PhVo{Rg@!fcQKOQ~>ZREE7ksKHCoj8=_X-FMB4V;Ob2hIe~N9Ka(gNu=Kz{TKukV)Wsz*CU1;8={+<|G_<40tMX4tOd!3z-Yf#hgjLOVkfU%|_lH!85Qeb2@mVs0LB(qFO}l5Vaj8xdXWs+yQPwwu9Ti>yZuM^<V?(1smWB<WImd^S~A0LZk~^2+lyx1ZRNLkmJB<;PJ==@Obb9WFmM1I2n02I2oLcyce7eo{Rh;crLgI`D1Vq_z{%k)yOsA)!=&M&%yOzKe7eff^+6aN#2H%ycyX6-VAO<wt-v0>qL1fVq#O{ZuPIp?>?qnu*yFwqra&>h9kdOCHfkBD0?d6<@pg8Lo7WIUZx)Y1J^(}ZU'

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
