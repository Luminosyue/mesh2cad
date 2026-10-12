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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e588c7566c54e4086511411763a3e29/part_000.stl', 'relative_path': '2e588c7566c54e4086511411763a3e29/part_000.stl', 'source_sha256': '93038227cba9264f74d59d3f559e1e3f6b1adf129fa2bc1840a60ad9ab28bf8a', 'input_faces': 320, 'input_vertices': 162, 'input_watertight': True, 'input_winding_consistent': True, 'input_bounds': [[0.03471563011407852, -0.41026735305786133, 0.11518251150846481], [0.08928575366735458, -0.1882454752922058, 0.16903497278690338]]}
GEOMETRY_BASE85 = 'c$}q~X>eB68OJY#MRwExal^|Z0SsFbR#`5nxCBDVBI3pyAR!20NdkxvykSuU6<LBTDi<rFR4R(?hg!=uMeKB@<CNBZ&>8#A6sFU$(`i51ag=GEdw<W#d(PNSr+sIh`TySk{B!2KcRA-dP*IlGA>T_s1H8YS8MOCoFVB<e?&W(Ms_Gh6EUl^^xq9uUc3$tqmyha!@&&Ui7Pa#>c$*8CRn;%8E1cvPPOhF%SmYO0uc>ROt6aT!P2I98@n=@9s;_GG>uW04R<(W~I%ZsPkzX>b$Zz!j$4}SRDFo9lo|q<cxitOr^Q{urk8Y9gA%0X_@GHw7@mnh&Ec)sr`5rsIcX@qFuCL>0KI{0J_x|}0Yn)8;8%aKJ{P@(*T5^3INAscMXUWIk4tvd-=hh`j-uuq><C?22xxSev`M~it9}HY?jpO(A)A=}lcF6Q!=KALPkk2~4SD5C5!GEyE2|NEWPR7AE_X|IA^JBLq<HSxr!uL*={m{x^J)Vr?<C{Ew;O3`(l>RO^kMF<!nU(k6T$+x9Z+<U+<mQ{dOXu(8ef*$$-RstU%p0CwAAIvX;CsvMd@ynRg=C(~?Y#QYSN%^~^J)C^`Q(1#oB7}ef3@@B*4kv85I@xWh3}PqY2|~nP3buJ=KkVGPTs4El5w*5I(~Lp>U%rhe#3gd$_J(6<D1`$A31sN(5J~bv6DA`<E~S=`RJYB{36#k?+bpo)y@Z1-(1M`&3y2^0d;R$<NrQP#_{pZ^M)Tg`S_CmadLf}y!z35)o)qX=flbAIQV9r!Oxtt^Wm2>l5xUwcHa2K)u(gw*_QUnI1#>iKJkMRJ0E?qI31_N&d2!K%e6nU#=m^&!{qyw)HnC*O6tc~?0op^jp;Z}Uj1OzmbY{B{@^poI2n9%zwrH9J0H*AosLs$=he@4-+RWIf6@MQ{ykFP<niMkc0L|*I2p(5Y3C#S?8TEmwyx*ZrgZ#IQs4Yu{P+_)A5V$Wah$yRnaSthv98b2Ey*|`zPZ0gQa|hD1NK>Oik;8k2UDE!|NdI~JUDp|-#@+b?Dzd%_1)haI(hwF5x%Y`5x(E~YkPd|i~8pJ<A-jZ`x3c%{Ge0QySaH!pErE7-r~njKIFNIoxJ+~vCi*(-}|Dz`@V!uKErzvIeC3wG7WpIe8_vPzWKfQv76WT+R3XQly*C3T_4sZ_09FckDPqKx)eKk^}WWOc3#(8d@~>XjFS&pS3@Ts;m76Q*m?GaEWQ~Z-=AaWJ@$oQj-A*2A}XtS-+G>Br~6urZ|*Pqoj1$Q>%OMGd4HQzKdk@M%Ikg|<D2V`pLOz)?#m5!KE}`X8}$=w{#(+%!YfF9lgIZ9?7a3Bfs@Z@AM*K5D<9DpMfm1^;m1zir!UGndG(_YerM&gr_#PI#&7G-Q$OqEwcqo8?&J^B?|o44Q|tQEmxivdeJOt1x|il7$Ip<DHqW!h(Y`u%eeJ99&2vaT>-ZV+(YM>Jak72V{y%p7nDc`A=DF4L0=}-#n$Ju<ZH=Snm(cM;&M)el=c>`po9BUicHhU=I6mhuZ@=wFoWIm>>)Y+T8K1oW^=J0{IX}97{HOH%7~q@hL*DgGe)SjjbHYBG!8i9&{0i%|A6>lAFKj)@OLb{I?N?Xk9Q8wv_~Cy%>aQsMua5d9#iRe<qyF61IXuu>^C;nk=tJ;A_+j)h_+fZ4x&&SfFGZ{2rSNj}ad<hr5?u|igx8>T@EW)t-2m6a8__4>jqql4E4&$g3f%@j1#d^6hPT7dpwGh3z<bc=;XUwPbRWDIK7cmE2jG{`Bk)V`G4vJq7<?R!;N$QK^kw)2{3?1Feic579)yp=htL<{L-2m|Ie0((0=f%+0p5-7fOo??(GcDVH=$eLCb$uO0&avip$+gRcs;rnUJtKBSHbJxTC@hPg;$`<;1zHcnt`j}O7s!95`GkY5PlS1gwBT-!3)rGcmX^Iy&s+fm!UJ^GWZ^J27C{ECps0r6P|`nf~UcEpyS{>;PGfNJRUAVN5UoWD0DbH3cej30^bf7q66VVco5nj9t7Wt-U#0c--PysZ-V=w*TMbZ>(QR@^>A;rE8H9Ij&_2(!`Gng;cMUys0Vj|+o5@IJGdj-8SV&oLA$|S;2vl%xCeYKnh#$K_dyHbKJX3b&F~HIEvOIQ0uMk3!vo;k(4p{c@G!Ip9tMv<N5doFF=#0~1|Ew}fXBiU(aG>ccnTW8Q{d_7UGQ}HZuDOGZumZQ7JMH(8=VV_&Vyy2t?<%)^&$8%N_Yt+Tuli-P6@B3gzG5b4V3Vcl<-zccpD}BG$s5jCHy=kypIxYri71B!mm)m5heUGC486?K1d0_NC`hj3GbqWcTmD1CA@_aeu5HipoG^_!mB9Z8cKK>C7hvzAEAUFq=e^F!sV3k{gm)bN_Yk(Je3ljL<x_hgo`QRk(BUoN_Yq*JdhIZPYK^h3HPOhucL%}Qo>y+;ZBrrdrDY8!g-W%XG*vmCESY=&ZmS6DB+taVV@EnObHLAgo`NQ(Ufp0B|L!=o=gb`l<-}Y@V%7qEJ}DT`heH=9{<2g-{sk`zWc(uJ_zd?BCP9-u&zbIx?TzEnkKC4p0KWs!n%G6>l!Pp>#(q{)xx@-3+tLMtowqn?j6FqzX<CdB&_?Cu<m8Ty59-wo+zyQrm*g<!n*$o>mDtv`?#>~^}^Z@2y4$EtbK*B_8!98p9pIYBdmRnu=Ya2+Aj%fPbI8<m$3F`!rH$HYmX<aeW0-Rio)7Y3Tw|PtbM7l_O8O(-wJCFEUbO9u=diz+HVVMPcE!|yRi25!rK1}>lr~<&k@3U))3b7h_Ieng!Nn_tY;r#Js%0{8A@2sS;Bf26V~&Zu%79J_1q_{XG38<KMLy^Q&`WT!g^K}UWm?vE6Uon&(HgJ|5e}i36o|l_do94zqF72xqtb$R>%A!Kt)+cSw~wJ(DupAe@mWt?_Z*jRI&'

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
