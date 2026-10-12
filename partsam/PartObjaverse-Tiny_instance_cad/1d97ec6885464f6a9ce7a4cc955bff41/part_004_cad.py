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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_004.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_004.stl', 'source_sha256': 'e0f4c0777e7275530ec65dea8c9da172b687cc9ffd930db9c797e04323bceb5f', 'input_faces': 180, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.1984208822250366, 3.4496562480926514, -0.2744840979576111], [-0.53086256980896, 3.8857500553131104, 0.35227617621421814]]}
GEOMETRY_BASE85 = 'c$}qJ3s6<p6}=BoK@mX^f<btK3MeW+4GQY@haXf>MDT|X5fB74V65n9->9uhwT+)xVlY08#+YU>5kZMoZ&2$8MT|9*CTgDXQ~#3qDO%I?-nEyl>9jMQ_RXBR>#eolKKtx-?!9MTQi7wCmm;6e%GMQU4=ZhSs1H}gOIeUrG(R^ptGHL;yb_b*4jvy~H;hXen>5*^EKn8)&&n#!EDG*#4vx!?2@W#{XU{E~UzAZeV{Xx`EQ62F$S=;)`Qq6b^Ro2sArTRgVdkjNF!K`g|M+RGmtZ*%_VBQNwflIwsrpsBbftWdezgTX``+L!5mjx$d#8S6@Ya?0gnzURymj5JN_>BCL-^<t<gpg6J!Hh2?;Qef3mlDjwQ@{3z8~H%{MYRfZ>w~yGvbvcJ0#EfRK%MTkL|_0wR0tYZnLYwTaJGGGw_}Az?(m=lz897qXuue6b@b)=m_2xaPd=vSC{ve{70j}E3Orv;d^tS<WH!VdaBH)kmshW<Y~Twd9`d?E#kg0fmbi@2Csbc<9o;-BE0>`4CGOU^*W6@o1cGY@Yc{o%xhoT@ehdiZUC=+^|s_s{uKRG<{S}z#Utr|MClpvWh;2~m-`T}Hg?g_XRn3em6#%_=hW~$25&E$FY!^+CI7f<>rtN~yt3_y<au+-apWI9N8%&b$h^0EG@uV7TYxv`H6q@+CEz6DwmV3?wWs(J6jWx!YgeB&AwE4+`aHiK@+iw5gIBMvK)l&@;Rx30^hn|-n%W_M;M#MjC*?YL`^@#SuVyBEj{I4T;I&D^WxX+-4x+y`pGp43frwX=HX&ZUv<bYD;wklie_%J_Ta`+l^u1E2XTHQIkCr^XO>MBQk1ni69XkgJe?<1PQga4%YQZ57kjE5<{I<KdjwAmwfAC6oNAUKub=Yr;`zyk4T_$|OqBHot+2Mig&mFQ42lTms{?|Rfk9n8=3H8{Prq*B|7L)gimi4ZVMZC4-0eG{MH~MKFvg?oN|67-Z*N({j_`?D4T5275yOW0es!P8L)Hh_8#IKS2(RQfzJo3MO`Yv?y9oauSZiz3ZgWzq=6_RI5kN41riVE=dh2!Kt{oozUt46Jr__S)oYnjXUVLb~Az^fPb%Ra2Dmvya4kvt932h~zohrSJrkUX1$(FaRO(HB^6zBhR58*WnP<@ZnE`@H*i5bsbX@t^z(@m9+@@QP`I?31TM8?gSW_k~Ysg?_51yd~am6?pUUZE}BgU3U)oed54tx6ezSWwq#!-Lm&K{JmZ#`)Yek8GfJe4tOm;T>6|c9sMzT`+>I=d?@Q3JFE)pzxl&0@Vhrk{7EbNquo0XUOiDM_t%2m*q_$aQt<YqGcxZIMZ<iJIpEE)f0I0W{ID+j0SE9}l_K>&d3p@%PriH;>#N)$dGZ4mVSiR%1g|d0lYYkZL>}Ao6B3`Mh>usCuz$4Zec+X;KNnxT>(9ck&8xs`<A+K=Z_chqUPp`YHD5^nho8uPc<3+luG}Ecfz=%vk=Msr;!W33r@grYo|9U=N%#??r9Yt__2_f?jX$FgXKQ6$qg=M5UrndM+rOM5_si^WQNLyWG4P7!CG~IIc?|V`ode$Hc^rAn4aK`q=ae+?*6-@%`C!`Hi2a}LDEV()mO8!jt5M&N*KZ)+?V$KlHbnMA#T&w(eJc6)1mV4AUsND`zok;oicwgX644*L+Cl0x59tQq?EziD+x~h**1PfDQskc+AbIY@$aCqpBk(@ezVroe-`H86OCCX}$5!GYd7in;^RTzC>^GM;uS@^a#K&FXvVWEr2!CglJkQHlpr1A$m+Rv5F6oc88t)gaRsnBy3J`yPx1b8^di>)x=yq4Bv$-7ik#hHm@QH^c&&3OPkK5k84c=awBk$i0?NO)NR0dvY%9Hq`IXH)?YaGB^_r^>8j(@>>+1}>PRouVUqsU{KYJ-oq-|PXeR?Bn4es{|U=x5qa@b<^f^4xQ)J&F3y#e!GX%X-!Op4gwZz(~o{`qxrVc;SA0Z|e)*x~{AAZD%R&7xk+R-=hC!IiFbOWx`)&y6{@L+!yNR><x%_SP9;qGEMs6^9=8O?JalV;~&bri>u|l6#d~9%-h*6`D@Po0`oa-5k8|v)}?I6{<oI<gI5Q}%l-cQ&2oM_|J)8fqp$4ehLY`vlYVk~4te|Y*d}M)34OTer|0a9myXT`37dHR_eba4=>P8M925Tk9-VvYHT2U*tUh}3+MC=!eGDTWM$O=c>m!jkk($Ac)<-gNGBtx6tB*;<lc*WoD1A&Io<PmGj?+g9v2mS7Ziqe-h!dz8Tz`GU5yw$8xL*1QCl04(a6R-9OdL$D2dq<+0O9~@2KS0SyokN18Jwp++7h>=W^nBl!+60i)C{hJKH3qtqh@fv`tT<9re<(~*pGtE)C?|6AKi(&QwyVS5yTPHdegT7!~>|s(zh|hW2g<IZ)wD7)Dr1iI&nI+Wcp?yworTF<uu}H)TYt5>BPo0lbqpO5^)l>1o}3Jco4NX`W8tXNiCedbs_FTEttM_BJM;jfWEmCyHoR`Z>@-1QEN-zS`xRU=0e|`iJhsnqi-I>9@M<)n?JEXH8Xt+Ar7I|oxVj8M^THQZz{1$Z2)~6PduL582UDYcm}mJ`ZkMr7PWNxmPMRJ?S+?_#F^AG>01V|am^)X_%@MvBDEy?Hkf!YwL$bPnmC$TBz+4a4x-kDzI7z-NUalnb0v1A=1$+7h@GglqHiW*6SbD~tp#xlYR>e{jo6Kv2YvG+_M_%c-?|ZZqZUHn`VjY_7DeBN5)Y-O(zjINRBGet+f3q_)Mn7PJmNfRv*_C#;yKh_c$rI_OD&haWfL3Md~$|wlZhu&n@Hc{iQ}marf+?T`%;UhZ(WJIQVXJQKEyuMI?}h+#I32h(l-ZU2Wn3AO(9mOndqA%u_Lt>^sNnX8)|O!?N#Desrk{jP~uQ(-RRqE#II57L*GUakDxY`zD*&XLM@fP<q+pkn@QgahzqFY(YHe4LTWF(%qPyLmQUYi6C2mL<P6`Y5>KTznZAuA9!V{pzQqv7P)kZMIe0n#r@tEi`LV*Jm;ZSD*I)khnDz262kN>0ap+1)Xwgzkc2Hh77L5#l2R&^Mzy'

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
