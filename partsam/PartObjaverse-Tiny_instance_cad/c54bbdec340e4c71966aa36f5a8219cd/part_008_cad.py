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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c54bbdec340e4c71966aa36f5a8219cd/part_008.stl', 'relative_path': 'c54bbdec340e4c71966aa36f5a8219cd/part_008.stl', 'source_sha256': '212778a6033ed37aad5b10a00f6bae9646a9a57c9ad7f474c7aff907d3993d32', 'input_faces': 124, 'input_vertices': 126, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07314595580101013, -0.06330814957618713, -0.11549809575080872], [0.2105734795331955, 0.22321471571922302, 0.006122836843132973]]}
GEOMETRY_BASE85 = 'c$}q}2~ZSQ8pm5e4T^~eiot^cbP>e^MPn4{j(Fe!!3!_c0T~cfL_h*6+IU1+58@F;S8>#cxB}kSR)qG7@rY%1v+AxfJH|Z{W4TE@YU5Ga>Hqg<7p&Q;t=*xf{=fdu*I$4A-s|^X6Fb7)!&{M$zhYauDLB?kQOvKG;;rP^GP6^s+p@Z)XXMpWn!-0fHM${YTy*TjdP<J6ASlU}H9a$^pCu?fxo=R2B`A4LW_D&m`m{NjNjB3Tk}xaF=Jc~>BxKl}$DKlZ_6f1{3J$U4TmHvSBWDTvp;L#eooeLWxTKmjohdCekL@v651Oi#Jil!ETJBE;=CQS4J$xgu9KPkx7ni~x?p2BSNn@^<zV$}PV&s{8tpa}a&xlv-`MP=RD2v;VJhPsNKi{5j9xEv^;wO%kJeiB(JNEV72mkLK;aeDQ-}<Nw`TbVIHxdWH*J6YBLX{}^_WF%*UG3PhQfR_a_)7JqMachhz#jOgr%9gF6S!Z?&Ek)6UG+MAt;1U6QDRee!yh(R>ZuAqI~dC<b|KG~_ay&cOOZz}tk{X)k1mot557UXw(vVU{PB<Eem%M@K|KTiv;%(kwUYm_=Q89;n_hzRe&==-dAvp<UUM|vhWL+n)X8s*s@e)oX?eAFe(iR}X7~js5wEi!b>9y+;rEVR5pRFtiFixdvh|2B{Dagv;}+tTrxokqcZjYNulvMf92r}lOMJ#pQcqmuN@z$r;&s-er+l7QyH3lC&bVL0QkIK)o~@AjdB2L%=}ML9pS8eO+(#~}?HeQ4OZ#}wmiX~Ib5$34^zE1PR9DyiL0zf3s<TgOq3Ytk?2+Z`R2S`FJXx|{b=7Vu8#bvf+Sv#$->kam7wzlwTWi-@(~m~CH@2xR`dxXJTB5obC;A6>cBn4Km1XyRyXs;bY6r`AsxHQ@rM!HX>SCO0#c8`$7te*G{kD%(7tfKU!+<@ii|5WBc?P}_`Mu0Dy047G8!bxVf4x-vn(^7XEqu)pfO*W)>$*IrUxkVP)h_tPXORW9eIvIO@>qFY{q|9be`S79ibM9oe`P+=D~sS8CAX1BubF4Ie<txBD?Y{V7t7|uulij4n7I;vFCFuwW!ZhnGs|1*e_6Bu{+@^8Kk$(F(qyUUZ%-vp;s&{|QO_45|MFG);QQUbi2FL{o{9L%gW?zGNj=Z*!`IeC@5k}+c*Gllp$UlZnFwF|y#u}$mIYtC<x_#U4=2D^q9*sk@4goJ+Nzu4YYX4P@yVl=(9AEyKbx3}<M0cWb@B`wol?j57>YXeGZL?iY<K{E`bPMQ=kR32k1B(&UEU#nyVa9TbsVXG5b?L_p?&m%#h72L=NpQ@r@yRsb7g(8{-v?_?S{*B2YO>(a6D-u{_a0Y`?QF`JmQ$(3ty{PD0!N6LBAV$?ZvN}BJl_8IchDxrhenerT1$4TJ&|Pe@byS##QcA@$Fm1|8{T|`g7U>$#X>&|5Lwk)ZgZj_!(hRf6?1XINrAO5cJ3k84u0Y%JY7$P<-tgeESTpccGi$YZF4H&R;p+M?DwHB;IqVjEDE1XTVQ8E%EKr5byYT4d!=yd+)=DU)~4t`tqf5rtf%KbOiAMg%?o&qW-AI;j>Zv9*sZ2d7C5GV7#T3z&8qd!&k~9KEVCH{9fYovyn&7k^O+yHtsn5j^CU`e76j&TlOC_#CJ<NhkX4WW1Z9Yt`NW1FU1cyT#SBnRKhoMe=B+XHx(g&#FwXVy_W&i(mwaF?&>S*{|0&d8yL_hC$O$t(*xiep`G9>v-iqA;BF82`nl&-=$AziSf};7Kc0pkweke|rR5^of5ZnMPVb*`5_uM1#XiOu^N#qQJK@`X4B7W2MT+0uhCB{iknC3m_dbL3=Xv0{vG@mKzh!lghOa-EAmeWTJnY+yoXHZu{1ZHv*11=)4^tM$OZ>{!5+7*8{!jT~71~jGcyl}a!#;;lPsvX4CvL$yqumI{zSG+5p!gdUtTT%CYxoZT!{RrOmpqeZVc)5DdMx8c3zvE7fpHXip`nZqeb6|>U%PV*{qEO7e4}Lo`r(U+<M0#Oh~Hy}4d-uci9C)M@5*yEwFv#E2XsD#->;;K{|`6xpZ?vFlc+x;SNvO6?8}sy8xU{Nb@6xQZO8rJxhsBpwd{9GjRR=k^ZIGzGcL*e{xnSPGyCbsi2wGX#OFRk`x<HE5N~b%So{U^;p<WBPFKg)c^m0nIde;F1LscF`So<ZjU*@3eidmTVKwUdRU|d+zkC%5`+r|WqMbDicYY`EYjPZQ7&(qSmKsYobsTvtIi5P198b1Vr;)AXB<gf>5_twSg*<~in>v#`o18(NL(U*)Q?tm~<UDFFIggxAT}aL+&!;XR&nM?l-y`RcGpX~)rp_g2lGCZP$m!%XYAQL6oJ_TmlgWwH1acyIDs>8ZDtQuhB6$*dJar6tJb5&A6nQi`iux`&iaeA$f;^NwggTNuggl5ELpF6Vc@R00I*=Smeut`&O^qPGLsqG8lT~tmYA>>>VdVbg0o2~)0pxIMPjWc9A2pQRkKC8qgWQ+=mh;<(+MU{i+@0K&+Kp^#2)Qe{3$-)33ptqDi5yH0qW*#$MD9rKK<-Emqy~@!$^KLe*`Mr3ZAbPax98X7w$wJ{wq#%Gn`B>dYpM^qHMteFCAk&Zo7#fxO>RzYMs7}SN_~Uel>9oi3E9-f<k!hwR8O)Oxe>J?xe@s_YJKu+<OWm^as#qE)s5^<u18hKu_NladAt9oe~tb7qnp8X{!#YonRS=3+GnnHCi>T+7CWLomNGZzpE;SmX|}BLPiAyqqW'

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
