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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_005.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_005.stl', 'source_sha256': '22aa4bfbfeec8e0bfb04fd4b686a002122003cbe1735c483e512d84c81edf214', 'input_faces': 272, 'input_vertices': 150, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.01586088165640831, -0.05343423783779144, -0.12404771149158478], [0.26848849654197693, 0.33857810497283936, 0.23535354435443878]]}
GEOMETRY_BASE85 = 'c$}qK2~?EV75)`>Tu@PPA4Nf25Jf@7$nOHUprX_bP$7bX8_1%fAV0DxA|i_>QE_SvN{mfi6OG29bzd<qQDd6Pv09teEoo|9`v2ekrX73Qb9&l2=brn0-@E^P@7??6&CHq5u?}^d6?t`5oL5g<S=>}n3~Q`7D@$UNQsQUFCVMSPOsl0hK{sADUpjvBxX|gflqJdvkC@ox*-0LQO&&w$4D{$_@|cs5l#&#^XjVc}Ost^?MK4H>)%E1K=)_o^ckesEyO+twvzIBu^gq5D=}WL&f1~)g?zJuz*8>dy^pe@|>h_j}&`0csu55K!3%z2ZX6WjmHqb5F-Ys~p@{ehTZkcfEn!(MJ{B|LJ|Gjf~zRkHj=%eRdfS&7i9(t-{vEfb8BQ7FeVRzB*9xFoLWwk%WIu7;_{mm~@@%-w^!aocX@4Yk;x>NUyuj$wFN|7i1I(Sr{S)%{aHXHupzKgHvm0QaVZ(Uo3bt;*&MgJi^3+r3|1=geF$3fS=dZ!Hjy8}nD|53RTUvo9c;88CJVE@|aEux2HMB(|%9WT75pLQ&ScRPl7YpGTA@x?2UC#CgS)bGyEq90n8iMma!fNrtr)w$@8Y28cYF&*l1LF#&}1p7?2V82><H|ayjT<DfZF2{}MtVMpZ?^l0Deaud#O9A$J_3pQzm*0`+-Tg)XrFa$irfTF-zM|gZ4{NagMo&*;{`;!ve>=Vj>+tS!%osPnnjm`d=aGoJoP7rKZVD6q!=~%7uMxLozYmk8euJ(^p6_nR{vV01JZ~Ng{pc?2S54X|`oORf?9-+C6!!6~QuJ?{C8B>#60lB_&wkO1u9RVY-c_<5pL3$0*t`&W#P$oX>F1MBPwTv+sK1)}Sk^hCa3jv~$dr@dxz8nje4kaQSIz`kPhLwoznb<A>J}J-^(f7{ioSJJKJpejU$WP=Wd~3P(*#F}JI#2{jjN%*y%lvcWp)$&%j#^bKROF_GY{=4y3>eUc=r<Y(H!J0^?R7H5k7l9`V|!#BJbC+<=C(K;;^j4GEVXgX({VByPQD&Gm}Iwbtym}qg$a4*32-;lUua`<Dp;U{bjk8Ectf6tU#WIbxuj2GFTra4d)~v7k!C(yh`+Y-g2M)I34x3gm0AmJ$<l#>&=N$_XyFIlI|<;{DK`apJSEy@QkgP_u9w5!}?deFM4GR@|!!H{ym;gy()Pu2UYmIR5?F3eMjW4v7b6`OC195vi_TJ9<0~8qA%)=UqpX#3HPBI5Fq!9O}F+A#yY<>WBq2Y+S32q?Qu^=&1!`>bA<zR^-iK0b(l7@+FsXkj+J6PXBS~#*3aD~&(l4N5uXx?I;#)7B|fa}yU-i>V85p7K#8xJu?70!oASPn4->s;JkF1{&?NVsP4D=pRK!2Zl=JrWbjkls)9qN#mWCGeDQ$-6(XBV(oK(1C{p!AW$@7!kGp4)-a<4sJE_%QQ+<Vq6&y!N8LdnzR`VPz+c?EftUKOGroPvE>YsDM`f4WQb$aK`rR5uBA&<a10{6XPKsMoi3<sR<(ThY_g^KnjghGW0xvb~~b_~ZO*_ckBLdS09my=%RA?C1Fd#78YWCH-pOLDo5F+Y#(5qekMFnUG(5X_fjf`cmSp<q~f_@e%Sgy)XKPtV*okb%E6L<zwg;H;4C7=R>y-fFF7y`L7;EA1y`oqz?HGm!Z4<Cd|;)9*@vpEw~|cOK>vsD0{x&i#Vl`#4ntMK5A;Mlk$FOCVFZE+_%cOo@eFUv=KdO0N&T?&Is&REAAwES!^8YdE|`T^JY)c51hjNZ)sbAbE{N&iJtN0PUH!Gh4m{}yhV>|w+-_ql%qbDszB&kpNHF|FZ)pkt;KYSA2=A_U!oq=NZ-$iu8rKc3;Dlq@(K9h2<WPR9L|Z7ep%{}JXhk6c0*s3n77a`wPm8{b3Vd(wpQIkJ=G^kqVMvlLcg+Ge2jH|v0T=3VK6=yw9rc2Z<ZC=qWcb!diwduc^<Nc@$X8WHLeE{pR-N$n%3`Q-lC5CFyG`4MUT$SF?4grCiF|ae?s~@|E`>q0B_XU((#JK7Y&ee(k&15vAEw5efMARJyB_$f_+))-I9HMwxAsIE;)nqujV+^Aika7TEwp!h5Jx@*rZ14@H6V8IC-Lv<`gH1_pd;I6~|9;o~?>&jeQ@Z;@ir3J1n~L>;USc6}V%ars<s}en8UO$m5!V^Jc!)OX6S5kk6@r_vD-`_7=V8Gu-p)k{{)s?CUFfego85JD>3>^gut!pEGbX_IurebEVE3F7X#!QMah)w{cFinL(nzGfch@+&?RII6{5r$N0QZ4(`YKvD^p|{qh5uSBt|rG-Za%yjPRZU-jffoFDa*84|x{Ccd|*pOxU8Xs==={-Xzox7;3sbE0%zEcz!AyAfX#gmYqwN)dhOUeqn>{dl>5Qc^|tO~d_ZzBxwDN!c2i*S!*bRK0xBFLU&E(Oo?7d8&4-EAhQ|K)2lUmGc&M4e`pQ4<!Cr2>POy?ZkPoR91`bcn@_}cV9vumEd#G)yI{%_bef1^u_emMTrl)BcD^v@1nnI{This5-6XKRc~QlZRbtd*XE;Gr{?hleY6IDEqU4&$UT#liTYd5-xdAc?YPG*Z#bZC>cbx-Pe*6m8<z5D^hIm@lj!by&|mG=aIDju_)PNDE<n8L{8Z^ndEG1U^<F^NLMKW7$&S!1d-8GLT7U4zddz{Y693o{eNhj1V_xNyo9I8Ul+U}rdLw_-H(sJYdnBLlo%-(!2z~9>>=V`PqS{1HrCUS&*X*2VyPvX#XuNFx-~W`2@Bd%@l<nu&@BjTNo2jp%NVg2#3|vfZV2#}H8;IjM7Dud+&(v*}Zj<PLMQr$3I~+%D;Hl(OnajX$a%>jyRPr^tt<^1+ei`vH&TYf9$PJuEp2l1TUdOSu#A)Ql-b%T51DBDPac&!4OK#wD@^a={%Q}@Y#|DlWe1>k(x-F$oCpP?QJ6uSf&Yl#~7ZFFZe(CfX#FKRk*KG`aC~+v~w&7^<NyMSVvE<>bUnu<~;ym5*bxWjAAx`1kHXKf#!k&cF&m_)g{Zi;tiC1%f>*-5~OE|X;=aZKbmk_TZFJ!Gs=u3%5>lUWleEP-2^NCl{=Mpa^UQE22JdE{QOuv*kNVoC24W$nx4&>Z697aBdIFNV-`FPeZkbVsDO5L(`n@hilcrI}e{dnR;;zh)h$+KC%Mf8cptGK@$`U2t{;+6E-#OsL*i1WyES*rs2^~A$;o2J_!;@RYePqM=+$mbK!CSFB8n%Xep`Q*l(?4_F@u`jtV=d|Hr<U@&liAR$MQ41g*O1?z5iMk~aN0LW!P8$v&pGzD`97Mj7+7jZq<i_5XbMFSuBG2NSHoSy9hd7IPCHV^0DvLgcxUX)*b#o^kOFo=9hJJw^o<=^6>sr8P2XTB5#|+#@w@$isBkoGxiP)XKuO0Rx_hPQTeAbWSejGD!ly38MQ|U($tHj;t``F=$<P({z51&oocml^pac>K`cLOJrCv$Eao=2X{p3I|9AYQ;)CDSh_Zm$?$4HU(PelW2Q@i_YF#KVaP6UUHuX8i`!4<~M?n@P9k^lgZn6St@DOx%gM4Y519iS=tk--$Rxw<)^yqaR4zkGLJZiC85bNZgHl3hOtJUL_vK{YB8vA&wvpp`T)h7m_bzt|_e39Oj7On891>)<w5w#68FjKg14?B=;fiK|GGUJ++p^KIAQQtFN0AaZ~d8#Lehi5;rGqO5C2j9kmw3&B^_B8=;#Uy(h6J=d|G#<o$>}iQAEfP#ZzqkKEW>F!yfY3FH$vw+)XVk072v96~;h+DPIEa^pXf2D-JT??~L5*n@t69qvNjh3gu?XPa@n8OIFls2E?i6{RkH9pbvgjp!TL;ritDnX3Vxb>g@a#|+$ExBj}h(03qqA$Fv1Xoua%-I%K(pY`XsKgT+7&&K|G)4xI7o47lDe>)sZ9?V?*`Rovm58;@Bd+O$@n>T$cVsGMJ^lj~MJ#xc0AvT_E%<;w?YsH$jX1xvXY*&A0*2J0hvf<w3y}2hBKI_484~`kQwr&o()uLC3L&w&t?d<TM{!0AkOEZFB`(yE6pM3pioBflQ^j!b=5f?hPuCZr*LACM4Z?y5wRsIeT+>xj'

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
