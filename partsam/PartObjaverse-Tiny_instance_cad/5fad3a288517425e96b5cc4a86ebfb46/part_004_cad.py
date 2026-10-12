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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fad3a288517425e96b5cc4a86ebfb46/part_004.stl', 'relative_path': '5fad3a288517425e96b5cc4a86ebfb46/part_004.stl', 'source_sha256': '688ef954d68826b85ed59c080362ba03f74dc00495ac29dc4308a59f9d15cede', 'input_faces': 240, 'input_vertices': 190, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22440537810325623, -0.22440533339977264, 0.04898977279663086], [0.22440537810325623, 0.22440548241138458, 0.6235123872756958]]}
GEOMETRY_BASE85 = 'c$}qKX^>UL8EuAjWDS8N5Y!7I!^|LoVNqb<JwOmaaR|f6;_?X0APmA}Pz<Qa6){RMs0@o>j1NJ=mPwF(3~*TjVW6UtRHgi3)r%=BRQ!=jV4yH%lJE3A{pj28CY3U;>eSbLZZBW={rYtGePxrHx9Fn6Ur)8V>&ew+os|OGsV-`1W$hF5=Tt7~zo=$eGu27+_!(O_dD{JDGn%QT>gj^Hl}qN-77X_aN~`WF=;swwEv|i{cJ`u27uU|M1V4WE!X=f$FL`WsO{L`f4jeY1pEszmpZBcyC4V=G3qjeD3&+KJ?fmLd@M+z?T?va%cf4K$-hcn{DezwPl=I*-8-u;at@4IXlXuG}HwSwYG39;oro2DrZ;hHSS)toWeQ^1AHlH&5OLzXk<r6XGeey|DzOg*y8>ZE1{|9v4Y4e%GA@8sLePg8jxoLHYnDXBFkT>PMrqZ)|y!}22BI6~WB5%eUTw(d*PXc>B4eyc9&gb=-U+a1P^T)gGc`$tP(#N~)@diy(PwVnmE(P{@4WA-!{7;ilUcD69<2Afb-jq+}cR8WkO_Xf6-<RQo5h1VEhT}4PW_ZZ^%O+lolqVm&A8jWys$_d2rv2oYkaycxV?*9;-y@%Gzlrn0@tN@&KDfehXWwtgr>{;uZO@P4)wPf}<q-$EU%pTCe$(c?k~i<y@ak&m*+fivkGv_LytqB&$9;B2x5N2y`Rsc6FyvFh>vCqjxID`z|8-M152rrbX3vk|{gWZ@zuEson@=`=v@H=={(Q)r@~Md@k7>T;7h83`3&nqo@NK@>ny~ovLmf4r{`;1CyI*Da%OP+2HN5(KOMN1a|3}E1b~4BO2JOe7ktgkWOCJsSwD9))q<i%^p#3Q5aMYgvEPs2*oA@+*ioA(W!zam`_zZf6d`8;0-<RRjg&}X+&z2`|+Bdu^3VGAMzb<c|=EoH^*z@nb5$bqmL8#Lv4wIXx`wOR>PsH#Z`K(@<eZuHHd3BBNX%^pu(WR^8XNG(>P7MD@$77MWBJYzo<^AgP9$kLI=C#MedHa*ir^+_3P1yX|Fpg9IWSp9KIK%iRpVfczO0|vXq(?qQKI_lWy<7Bq{mYCUwm+$p+=sZIWc7!9aE|*A^+W~SpU#&zM&g-#Kt8*FeY$-4F+JXJKUW*V_htB`;XmN}YCWi2^V7>O*zxT0Sv_gqb_)1R?dpimsFf8Hb@?_;C+v0%pK2ZQCT_Fk$(y)!c@wwEy5COF{K?|Lj@xw46GOp!FL$fA=Q+4k-3+`sRUFuQlHC7*GXC4^TD3p>=~3{ncB{AJB>T&6I$^In^Yh4O{daidKU^&Z-zMbEy7t!8<l(&K$vpoz-lLzH-5pBx`E1IO3${OoPaEE>#}hoqIPqq9H{SeHJl{C+mOjn$PP{3Ja~;2*MdRG?{$FS8h^)Ia;eL>G)?Gk8?XJ7CA@4cs&hSZh-N|~_?c5X90qBW-?&wTFKA4%SOS=5SQT<6@3wh7cALyR8)lvO4ysL-MPtC{Zs;=kis_3>Jhojp`!;dd&h{U<<FM1r#K4tifvrid5?d(&A_nmzzMLy~5Q-)X0K9w!+>{EtM6-M`|r0mO@clPBJ`J}TiV}IB7a`c?w8U9N2oRBp9=h5>(ntb|t^!$MHiJrF>(Q^yVIl7<Ix#uNqPvxGMborR`k{*9!^t_ajbDDncocCNltHT#VK67{UyqCk9^GtDgKS{@&SG6B8=T+Ta%z0Ih%RR3)h4%-~Id2<2<D9pB^1gH4Hhge3dfvu4U-P4K?<3mA+()#(G4~POZp?i|`yX>3(ROt1eMFCMOzwR|+cDAm2<~O!{O8`+bb05#mLad4`<mfB=e~w}qP8*jN5k9kfP1LU$J|eKdG~(W#PTusU+uqh|HVC8m-|)jeO&YJ<=)3N|C`+VxXz!8-pBDBK>HK(Jwf{w^F2Y2Z(#2C1U;_<qu&#t@0ySK9-`l4%=ZvoKjwRg?#KBag6}Z;dCd12-M;;OrY!O`YDoU{u|ZoYD#%w|RMl+jQxr)2jE(;kHGlB`^eL)j@c;cO>OF*j0B5c|L4)9R<_`;w5PJkaCpHK+3g!!*7CgiJGQo1@(Z(j`%LUVzuNVA+Kws#8uHXg19KjC-+n9d`^UVAf!E?;75X@r!A;ECwM+mwz|4qRy%-<>)#e9POAU~4n@9-J&H?t0GH?{>kjD5h)WZ$qpeS&?9zQS(h7+_bjpOx%upWv5*cLi$%dj+ouUgfiQnMe9H!M6kmmpcUgn8r86{(|<_^LFH`1!aN-g8Kwh1d{~c<+BCMBV8j{BA6<eEV!TPZwqP#k6X_dlK+`tvtYYmso)L4lY$@d8TeJ?k)I&=x?qT4Fw<WX+#|TndftnCPXU&bCm1B?Dku?*<1>$Wq{j=sC)g=?Q}7h+PXsTMUrlZYdBg)^2yusBOF=Ug#y@OxK_}X;2zt}rE*PW2xF0JRP3~?%A94jMjCXK|`3~ed3R=*jKg2!aA8QY51?%WBVhr2s!}=`<MIZC%Upajn%`|{DxPjP1?lAjlAnMuY>+CO&eYLRK?rpWXhix2Y{XEv|WBFtHIm*6_b{tkWv||tbn$P+e^G0&;`x$cZYdJZzyNR69j(Ylm_XoXrffjnPjTU;5rp3E{juv_`ixzq@oECb~ofh$N3oZ0w6fOG0Ivz=G4$B!W>CXJkY!~@%><{^2^aJ^s^bdKTek1=D$AkP<_JKUK19||hfOf2*MIO5G8lS&H4r%BD^a0uc-ME8k=tev1S$pQ82ha*=$9=TOLpN&pd=fdNp$pIlXajU(GSkqFh1RpjnTHlY6QCVSX_1F+tm1RnC&@z>pbyXn=*AGHp&PxdXSXpAJ%Cm~I|k7r58W8g=OyHjhHgL`pb<|o51oK+>`*r}Whe89E5zAc0x@wbfw&n#AhuQzTUhTM)>*;wBbdey>kgWb$2>Hs6Z6oZ-poUTpbc0%SVN=v3>wsj&!9o&d<G5bz-I;Q2YG1F0EIidQV%c<d#_-(V3*(k)3ApGcPe~aQ)(X5u*HHIf*%OhG7VcHc!~87F%7$3@Kx3?W*Ro1ZTwWQpXvQ<E5-WjnO@JnJF|X1)3B}C#@m8}Odn)hl>&VCDPkJ7iYTHVRkUcom7uSnkm*9Uzn1MCU>degu#WZTF+GpIwqgC&Ot+@56|7&!H0*=)cOB~<q&-9*+pumCZ83eUVBNm7h4k?t>+Yw8uXpi1RWMz_dU)qA(vMxVDE|$X>&tXsjt6C@v%eQ<QKtvXwPLyz{eGVFUd413$B8zE(&y>45At30VBJ#MBEH+_S@&()gKVQS=XWSA+Im*-W5E+l!!8nhU+}14Hq)?+1p`&M9`0otcB0^6)?dUl>?4A*NzL-QH2+V3Mc?@OSk#d}rrny+YlB^LjkJ}$M3hZxi8&Q<$kW2S3OkPaHyQQv1p'

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
