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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_001.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_001.stl', 'source_sha256': '0ab82a53a19ce50d8cc679a01f03217f7f674411f2d59031cc6a4e22410f06bb', 'input_faces': 78, 'input_vertices': 107, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.9757106304168701, 4.5842204093933105, -1.3889210224151611], [2.4857475757598877, 7.100393772125244, 0.4820104241371155]]}
GEOMETRY_BASE85 = 'c$}q|2~btn8OQHqF@k~-At1P16Oc7V0u@A-D=IFCc?2OE6)wVKNk9=SohCB9Q6|x}vYAPSXyqwtVk0e8lUfyhib`BaDA5QK%yq#vb&1NJ*mM5hG0{#s(`g^`pYNRC{oZ%J^PS~gjIq`>&JumbNUv8OS616g64zkKSt>N;FV9Xh6^vVw_gjPXG&uh}vg_s~#u?`uq(bRU?{rf^TE2If>>ZvF>K!0^XDrQMo}aoTWodr8iSwA$oB|W$1zD+iCf4@}93K)O2l)obMe_gn;aON#Zg_Z*S>3VGN#XsViFbKlalO#bttICV&YUY1ueb2N<{S#HZg>w|j(h(Gc!@9ZBbngZj;}7DAK?J5y|kVDCp~qF_vKs3ecYOzbKN<Y=3955pJD{pBa)DhVmq-D`HYMLmlUgKIM*98&LF;jM=zc)a|f5I4<AFELKR#tXm>$Adxz@qTV)Tf?cI-j^y;WO_=O(t0e`lA80uiR><Z#+@&Q+p+GyO#Grs{Z+1rggZ_ftTD%b5qoT__Wh%>~A`1|pf;or3aTurXPxaM~q4x+y6)4`>naH?D2l-n5ZTb2BqR#1IBk9>mhmd^z@2aI*6dKRPpmX<-_mOZ~l{z}BG>xi3RLj6>i)yT(kyR;g7&@^z%&C=oU-&eIWireSAA7GryZgA<ETP^2Wa6P!1{tog~FZy4CU(R9j-~XW-{AbrJNBrLP;L`5Rt{As$3hJO<`+)qDY_Tp%c3Ug_T$X?<W0PoI?BDwmeu<s;@x5b*;4clx!9KBc)`M%ujFeA#Q5))V`iFbq4&_w0n1$<+|Ily1mEz5aV{s0<2tTh~;QIYqs>2Qczek~-rQqtYXyS)6>p0idg%tnCwTPo9*nN(1i{dGc*BaD8%Qc{G%H>$%>f7*_|6GA{q?EW(KK;F@kF<DEE%wiAuH^3*?SXNfwqbqMd6&P3f5&1v7vDLF`Rm~FfgOmWO>%2OeO%1oYG@Jdle#^~M|wLOTr+N__3idN0UkStc>NIMuWTy2ia0B$f?Gm6iEmlZ%>C7Uku+{)0>(Ap+_W9_@tjC}Z7%ZH{YQO=`MecG{DcwtD6zq}kl)4t%5&)z#8IrQkdNBuO8I=|K-^wAi9CX9a6jos(`jC-3+cSvc#iI^J<YVw4=lrZ*Xq{&6YKdw2=ce===lP9*3P;Ee%y#U$O${oVxNpm1DDQUp#A*&$V2eo=6o0H*^-TX^s<%pm`~CHa5?K5&FiC^_3$sc3~ou^g81r$f1Ct2+yd9n52k(cyNaWj|5n5I@c(o-?T5%uu%DHjU~na+8TFJ_t@;S_&&vfjH)f0g-(T4X|25SVr!5U!>2LTJb=&?masM$?ha$go;4}Ncr4<Im*REc*pno;t9{h*2)B48LAWzGyW^n0j8|CxnpFYO<Z8!(6T_2BewQ5Jy-x7BRT$vmOF6V8-{#2Ge1Xm~Y(fv?71No?Rb@$;v)g5)S#J`ApSnZnj0QszWK=*^i_Y2hDbt|~6N7H?>wix-F^VW4DPT4u^2PJC*&Z)dBp$pIV+0wqc?uh$GZY8ce?8p5n*<AS$ewiD=<*?bbzP%S4Fi-oT-H6{9N%vC3IsD#P21kQyiMDiaygLo|hE{GO|K=EQb3--mF)cZRcyJZv|2OX=bPr~NODzW4&xKQ4;g{PAE?1qV-!+FFn^4CNs~$WreS_xZ9gcjo&_HmhWIg7kZT%zmiFs}%`8N)r`*WLq8uK6cn_k$FGicm^OGgoZ)xkd0qqv98MV?&=_{me?vJ>57%IZ5<cm0fQKlsigbPqS3eFNj}9!>mXA6l2##rQqd??!`b1wHip^_N|AeovNz>xB>L{+!uC`=L_$0leS>;;4S*?U>Ja8*sI!iGHuQbYZ>p=~X`>|M0&OuULZfrA2=YuFf;ldroxgdDN>p>ml;=45NGXO8YMCzqoM{#%mc%^G&J!3j6<+1>jQE0`d=WJb-n)R1B_o+@^ZY^1`~S%3*L>`3(MYWg*?G@AMnspY$okKQsdMu|zpqVch&=TKCeR7SwC&XmGt=qIEenum=7onyleJc{sfnoi@~9{$E}M*ItOH_meWOGY5@Nyv1%bCs}-KB#Fz8y~SpvKK2UBA^$wGzx)cD9sFOt!iI$YpKq|T{UDaZ2&Q4e^1dUJE7M3OchTn7o5_l4fSBq4(SMq0Ak$M!2GQo$MzpzgV6qpM_n&1N!sH<=@ADFRinfPndx$*jM9fEH@V+&ZKU0v%o!il(ZOh~&@qZ)84j1h)OfF1rqRs7dOkPaSGmRH|#C(_nMLSUV@b)Oa=a_tjc-xO@9Mg+TV}*G81@U~0@bMGv0H$X|tf9hZlwebtrZ7bcMF<wmG=b??LcBduJdYMW(V`#DG>2(E(`;dR{}ra`OfNGTh2{MjOi9AVKh}R)Sk4xSHn+*bnnXKUv{RWDGNmx33(NbjGEHNe$uwD5-k-&kz!byul4x@~k10cZf3dI`B4!xVB&H}~c|U|n5%Uih3KfihFPrH#VR=7`DUnGPbBh=4MdBGBGfmj6$G&3{F}TeXZB?`v31y1siK33N!X}Dwc)b@e%@vmS<Al$2;XhqG=WS!G!OGeCKmDux^GD-{<B5Nq|NWa!UQdsI^B9Zu(`99hwZ%ENVt>n+_2s8j`WM*4oq_'

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
