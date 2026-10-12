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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3acbbe6269234a22b93f7e44aa8b1798/part_003.stl', 'relative_path': '3acbbe6269234a22b93f7e44aa8b1798/part_003.stl', 'source_sha256': '9688e445ee0c263e135784a324935d0f4185e8645fe4ed17df16bca129b70a47', 'input_faces': 223, 'input_vertices': 168, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09811639785766602, -0.008558183908462524, -0.48840564489364624], [0.09811873733997345, 0.05131499469280243, 0.33559975028038025]]}
GEOMETRY_BASE85 = 'c$}qK3shBA8a}9K2q`I<X~8K?e4r_qVk8`VBA8OX@IhS$E)R`|7ZVB1qmx)>_#!kBJX|GvX!5v#I#y?NT1;t<Y0qWat(j?Ta+WpOa;CAGz4!ke+neRAHEV{ozV&_gyZik6-~T>mpS>@sDV@87Y4mrO=8bQxH9|FwBSZ_+mb*R6@-p4UBMOR21GG@#^FN2T&6x9G>iht0xmFgL<u1<jMBcAQK9C(78Kp;N7kZX?G726o^kliYKPBU_VmI@Pb2EzE?DODJV`8K9m?2U6D*b=_>&|l+9Devs&R5FUa5hH1cshZxmD}@>@QtbD-*f5@!p{#Tzh92<%@4e1xbO0GQ`=h+?{VMsbUq}<w}U2pCO)sb+D86MPw;leZ-<F~wO2oCliRy4e@gkh-rgqnYXp5s`NU+AZ{&$M{zdJlM7-4l$=7;3B;ronBI4Lpq3{PxPmto+M=!N1`4oM9fq&Nf)GNM!rCY=?BWe`iJig;yk<aAPRyj|*d!iVxD=n{89+x(In22vIncphsuQmFF?>`f$`1ap*k>_>4+f7ycvwra*8t;#vx5(|yHK!?`@MA4<9n9olk&iz3NQ+ztbKCdlMZQt3E%Laun{z}yR+5+eza~8|`b$VVDe}rIZ;|scBdSk`>&gqr@Ba_cUc311JEDC<GWi>Rt`KqJKNtC%?~Ne;ZnHwp-}O}=C5|1MMRl9r?i2pGnp(MEEBByJ&c`Y{aEk8RedNEDE8>`wVkwSi5BVRZQG7Fy>R(o^#4(?}cAoOy<h#*)nRR7~Z+0#ezWvEe@<&{xem^=W>gNB;MDlxX^NM~G=L+Atl%V+LPhCabj4n}XoW6Bpyk^iqpHiQ<+eMyw>cwWcKH6I+$baf+vpino$os-Ks~Vc+e)Y$qMLy=<z2sl>Ql6tfd0Sj(!9Q_stMGp;rst)(lKeiq$e%un>U?xF`7N*4%5|_lUP1ol=Y(&3aY~F!{~=Au$9(Mq-Ji?8Z4&<ZkUG)+g>T4jJxu;L*DTR*$R^>tPSrQbakQj#nn!n8qu?1myi|vLigR^cgQ!Pv>`Nj}M6~d&;8k^^{de)Ni1rH?iu|>b81kKUZ)@fU;`@@tyM=EB&k}LY7oQdLz8t=@-VRxGM)56uhKL*ai15vt<lRdAk|#ubyBfatT~RmP{}ruo2k+l4KflHu38G*9*iiDbA~uP-PmiZ{d*F^*xej*Z6tT`2@1)eq_rG1yRkSx&Uf3zu!Cd1K&zI{rV=I;Wt#O>l$M3(bQn}xn#|mHn^v>q^8;r{pQ$T)pB>B@4sSZ!}txUK<99LQ_`5pST3qISKAmwQzPrv<sjpAR86Zf+#dpcc@@%k}df9SL1cc_p5<*&(io|pcI=slG_Y<GfGXB&04ljF$8ytptg{xK=!qYf_A!HR{C`86=VTCXMK<G#`^(0%1{eCNH1`|7&i;l8qt$JELFnz(Pxb*t*+`k1)S_0e7TD0K)(r1g1k;)_Z>_n#5#m1S7_l=i)ki09h4<a$+Uzr8oT7gA#OEB$V)s2BB_nYdq$W4(Ee*26)I8kF|0wTgMv#+M7f<MZpv_`E@mV|=(<#PRRSZWQgmpDf~718V7hc%`gSX^-{6e@A(f+^=hV60L_ryiIa@Gi5!E>!<oA`95*hAODw!$?vdUY4zWd-(h{zht6-7<2dV~)hnO;qM}_Q&heA9j&*sQe5|WB)>Z9Ko5{yItbL4i_>Yz3cU-qm?j;}Vzi}U}|K@4<9oPRi8k9UOyhn83(PriOb>2HoA2uuV8*vZKuX(Xqd9LyP(n`J||K)k&IW=}(rup?;A-`z_#mD>I8aL1<{0{F&dsr0tc%N#w)B9A59O;wmV|Lm|`G*<g|Na2w6Ed3CJ;!(E_h))vn>{BfzA=H`?`A-%+Ar#V-5+a-d9)^%(fj>eA^GX1@U^P#qF?Py8TlRd8|INss^38S6K#Jr`B>jH>}O2x9-lHV*#GFY`^d+BNkcvL%?Fh@`byeg`HS0q%6#dxA2Z!&$zQs@N*<T7=$ucvKVy5)K5*V=O8sqTpE>EWQa5K_Tx0&F%&$`)Yd~;|Qnz=O2;aW_wida)f&HZR&k^Kf|EaB|{iptMGWpoA+Ssq!2MUxpCib^_)!G)N&ZvV`x>ITI<YN?h$;ZCh8LyV!O1^Wx2%&wro_2(M?AtZ$+qId;;N!f5eZD>Lix&BQaK`2OA+S~Ujqm7uaou<J&p2OL)$^71&VA*7I*)w3cg$IIuF;m4lJA_?a1PR@*0jpw(tbzhCS!cP;_IvEoMrs&lH%KiIG4Q<+9ub*#yQUA>)R&R!N9psUzpXV<eyIGME%e0ZE~JY9P7igZSuHmoI_pvueQngSU9)pwVe-9e0ra1gK%E<!guz2IRBb2bW_^<s|SelvQ-&;NXZB1Yhz~kVWrOeoSv%u`f#+uzw8P-({luAVOn;E^wYzY?$pfT8~^l>H~PQ&=^;8g=KuZa;Wm~-UtTxxUC=so1b7H^1oS9|(cmbCVc<dFQP88%eh~OhXwLUQ=P;~cC}xPpHQC@C=p1~{wTEFfLoRqJbOk;?1@=H^<61Yg8~sE>$1n^97lPf;Zd}WC0mE{J67WiB&d)%XqTM=h33LhCtV4T#{nOy}&;_`D1;)a2|24pM8Q2586yN27%b?59CKr8{qu+JVr9e5ZD@T7^-^(zNVI(*bdL;Bj@FeJo&`IE_(3~HKPJ+$@KLO2oG4#FYV?1~w^myopz)8@H!Fk{$Ddu{7zaI5n3@(7?{2=s$QoI7x{xOCua1M9{G@qwUn8TIO&ww{WKLcG3Y({-Ko6r@|tHEoaS3@ra=RoHmho!&@%-0IcCD)Y<&ocA|_lF+La0kQf0N1_1q0pRfg6;>t1$-0qc7`VzHZUv$4+b_!@i^ZNa6KI0Iv>0NdIMtSBj$7PI9EY$fZh&py&K^AdGJQ)yV2hOfa?*^oL2!{F98pS9*$g=0QqQ}k36}a!H~j`0C1fMUJK1R96ABq4;&8N54sl+F3nLmY7mZC&jD*O)+*?Y;1uW-<i~X->fziI{V|WXK=(s#{cz0;=#Ak1(ESl(BlvmfT@2e8g27?XTku^Ua4>XFh8}1a#L$(Y8$%bg=>ZOd?t{-a16&7!yFhnEEDan89f&rL4w2$;y%Ssw&Djgx9eKrp?}v_qo(-M_T?4kjv!HoRUSQaPvGZ}=3Vkd59nf3BVbEc?ek*tfG>==yPz!$-`ry15nt#6!ZEB&t;JwgWFxFjQFSHkJxPF*nCc`*zJoGqdr`|!RWf1%jARcv%$MsH)tC3eV{95qC(A_WxLEt#(AZRCtI9wBlx<3reMjQ)V19s+WGD9lE6!0AAJ>Yuq9O!!J7a2M+#4>bd2mnt3$3k;{0D1~E?{gtTI)jU0EW-qbxd7MGzy>tu>Ci<CzhcM)yP&6`&0O$2XwLJc_*|!f7eS{%F91IZy#P8LoC%$Yez|^xA%kHI_&(@#jB^1vS&EsAK2uWyI)!!qPyep_<<H~=R{nX{@k({8EnoR0i*<eDothHJ*9kUxoy5!Y0AJCxe*-!J&y)'

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
