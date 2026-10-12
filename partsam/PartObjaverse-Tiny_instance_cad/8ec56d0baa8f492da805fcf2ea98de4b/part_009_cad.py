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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_009.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_009.stl', 'source_sha256': 'b75055ca16863a8a0364244fc149a5f597c13d8d09d215b11cf90b0fb8cb3a7c', 'input_faces': 152, 'input_vertices': 97, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2676714062690735, 0.13761669397354126, 0.12556585669517517], [-0.022268444299697876, 0.15619921684265137, 0.37096884846687317]]}
GEOMETRY_BASE85 = 'c$}q}c}x^n9LI-C1O&NMP{iSo1wlk`IaO9ss35pdk8&tW6s##81-zm(W7DcN_K((-N>lAd#3<TWD#mCL7q=qHAyz?ZVq8pPqN#1#iY?kS-Fff3>-#lr(zKgQKA-*a=Dpwi-t6uKeU6i}zr<f5Qt9AG(?K^$Qjal`zqF;is%G8l^6J<Po3=Yh-Yi#NHXg`Zma8vxkhVxWG;7MMS669LWzFo0WKE2$sn}RmQ&qO1bYs<;ay8E^tE?`!=GCv4Z7R3Ek4#C5krSd~<XZW^zTB-P==Ox%ykw<Pd8j>I<@Vv;bRpLb^;{Nnss3r7nj1BZX7#<Le}w1l_xr?ojE}y*Ddx6$Y`GHGLgq2%4Y6F;c$mzi+zr1j=JtA!E2sCcTw4AIn@0+9xuMe3QbXofRxjl9?9L|Rm9Q(k&WBz!KX`zTU(<F&tVj2D%xy8Z)nm&|!&NuPbvgL+@$0_r73a5vhp{>>p`E?r{F3K`D`IY&-<B(Wtz;fU{opOO&hV~Yaa~i>#11z8SQTA&Xb10eyeG{YR&}xQ<~u#4pRPyQJeG5oZZdwxT(+)Ze|0zM&s)-fnA`h<T=^ljoAhVxy?(Zik4)y5pSpIk^FD0uBKwlJmyeH@yTo;6?Z=nJ+_tVQH%9$<o!k!%4|rXL+pd%Adbggh-<V5s-R4t#A9rV5BlQf`uzfML#dVT>^i8`X=JtKG<y!AfQcs8v%PrF7tE8TSle}-k&pODyjA~$gFpd~INdG6)nZ(@Qf8-|fdmZAsy5uJ;H>}Sm^IP_tcwZm4T_O3;4>+e7%%uNMFWwPzd;gIe%*AGMf4Y3Ya%G#|O!^!Y&hu#rBsZ40@%t+0aXT3wx05rgo8-pSOjeiScT+p*^V&*wy_U~f+r|1#`+P}mtKXI@C%<YV{WtaV{vWNoNb+AEvO4A8rd|}+H5}6O>)QWoE4fc%caq$GpCFfxXSb5;oxJF4R#)xW3ncGJ;^+AXUJ%!n;wt$%j)UjPek}<gxqZKoEBDWwBiH5Z$*$L+J$#nj|9iFkdnP5D<fi85Y`p1UNeihbY&q{w-Sab~p1V6pZm$QqR6Ot{xexnmc^_7eG?RML&Fp(gIbv=m_glj)eqKdEv$(Et%ljm^|4t#7!nS@P&TqKpdyVBk`F&3Mlen3EKPX=FPLV!@27JTv^5adU&eL_>?C+6pG>LV}-<@akNQ24=GXB}Ut1Pc6I6?ZBFmPMU?R~T5yFAD|vSVT&yI=AekCA<eSj*@CXlo<+T!bf*-2S;huJpcWApKci%dS`I2|hyl6XVRTS1If<l6~28l#hQ$Yb14^SitI(PQ5rRuB+>A;p3kjIYj2^@8Z8-Pab_jK1aqDmP;Eytry2DdD(paeLZ#Jc+1Yked&7gRCnoKQ>f9^daCtsvp&^TlnIY?YRHxW|NfC~-K>B0NH<d(|39DU+>5L=lv<D1aHw7ku7nrE3&CaZLU=y72%Znm0_VcB;B&xP@Hy}Va2h-T9t}=`N5f^%4=%&UgKqHga1YQC?g1YSy1+-n-9az7JKPtX2=|2tfm7i@@Ca}QJOUmEroiLi$>0KbGCTv+!!zKyU=h3sdzp(v^*kJ^F9nO?OW{kvLiiH+VlW@R7(O4&g3pJ~2Is(M!{fmOcsx7?jE2X+LqQoH3ZDdyhfji!13lp5;A6qj@Ud`z&>ij%p8)#8C%{9%Ab1E|14h6#@R?v7d?q{zOok`H=YbjUdGJ@jTzD?_QgwCT)qCPq9I9u6Dez2q8aM-<29E`&!eim#;6!*hJP`DP2f{r;7q}<f8FYj@!yQ03xC7i3^n<&?eZVPjA9yf04IT`S0%yUa;ECW|cp_W}E`saeIp8vQ4txc;621by3M_@Mf*ZghxB*@Q>fw6qWeE<|3vj5u5X^)xgr|aO@KpG8Fcv-?9tMWP!{7m6AUps*2K0oFfjfcDa3{C~I!G^Hs*eI);iKT*pby*|J{b&#PliW=QSeB(7EFX|;pw0bo(|6jbKu$V<?3GKI5_${{nNi}UcMA|k>Wpa{(2^TED+Beu)eiFB<OQo)P7h$7>?4LRyM0wF8vAE*{Y}'

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
