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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6499bf2bcc024d419bd23f4d2eb332ce/part_007.stl', 'relative_path': '6499bf2bcc024d419bd23f4d2eb332ce/part_007.stl', 'source_sha256': '2b779b21591de25c54080b7fcd6d23497fde0b5ea067df275ca5179b8134cf00', 'input_faces': 252, 'input_vertices': 198, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18866674602031708, -0.05748005211353302, -0.43380749225616455], [-0.013340490870177746, 0.16562433540821075, 0.22432537376880646]]}
GEOMETRY_BASE85 = 'c$}q~2UJy87KSfaup{>F)2N_=4I6@b?VVsRG5Rdn6$E=3A8PC+7E}b`Sr8Q)C~DNeRj?CdjEY#oi$+Z}m}rb8ws~j&zlJw!X02H>Z>_!lkKfHc`<#0&=YRoSa^)_e;ZsGsxN`aMqQx~$MIo((HYG4*(&%A<p>-w%Pj}LaimyH&bd7)SZUOzBv?<z5_u+w|!$RDfncV$GG<EkhxsM16nG`Z)!r-8g;epC;KV)2JpxqB0H6%FD{<TMapQfHB@0y;b*{1*TQ^4MW*|)~o6uVk%6?TYvSGg`)v8wp`ibLX?iVkz|Epwi2S8B{CF23=;qWIbq*Esq5?t0`~D<HqhHu&BH#n)Sv7vJy=*ePG%_7vazNomx1eO7#}&PWH}a@R-3H5XnWzHN93<iGq~>g(}w@E;UG{qS3{^6$Nz;g89WdF_poI$A^z^tr+r`Ijaj-y;Nl)^&m(HEoxy!{~;XZ}7V_@_pkkiEsFg7T=Wk8vfjLSvURQLG=Irj`*7C?H0+K`wac)Hu!Z@wn_feL8$Y|E%?1RO1|ZAI`UI*z#kgCRs8I7nWDop#W!-Ti<deXO|Iwk^+#U&TPpRqoZK>pZ|Qzjd}IF!_}OPse_^qGl5fj$@Qr3u6U3jnSA6TYX~_RaH}n}5i#`(!)SuRG3%<`;`ZNwFA;0yvn?>i`!a5Jy3EwkokJOLImiiz4pNl3+pY0;W*WSm$pMN(-*2}j!)*&?p<AztkxVAY`U(2%z`EIwOvEF6SPi!Ro*+ZlsJ@t^}Ti1laU;gJNnNQU};Fp>OKP7#)^mFA;^m8*5enhp6^1M6GK>e8^@N2qazNgpVxm1`4|MAdB8TZ8|$+w1$<T@0K5Whul@wN7YF|V#}NoqWk@%8zZIeg=fB=K$Yli;80k2?1Pq<>5GOW0R+0+1g$;E+7OCA%cw8q^K>J8Ex`yax5q4}E>xxPy`xl_vS72w&7mJR;*-*SEVM<NGvo?DP9>;+rZoM*WL<*Gat@8>GG|rXK2ddM5pt>PMp=n-}t5Tt1+_HXl7Jz8>c3(7&mLkJL9#)<piuU)D<B6(?ao4D)d4-xSbO^0nCN$S?OeO7y`#?2`|^ws5_C|4)VS9QV6A^l7e9OX^s<7eW3VXBk&N@hP6ynu5rmx*zMX>#F3NujF%>*N1*S`rj7BbG&yO^?lx-7T>vp<Xg+0$2#12E52T-H`ZbGY0T^0bMX!LkuqO%yDU5x%M;Y`ExR83J{#}pg8TFbt&w#L^+Nxn@1TDAW9*ZG2hgY24TpYgs{+Kgx?U6CGW{FO%l#&v%g{vRPyT(ijMotBX*;t6ea>%%=ez7X>=UmT_+1xb-LCFSm-)IzqM!R&*oO&+#J4<Ihx|r0rBB=EG2$Cd7sG$s9M8Q+lK8ewbKu`SiRT!<KzuF#SoFVYGy3nh3;7RgqyK^HrpWl-KjOUzEf2rzn-KBCQ?Q@6zB?uUtP{afuLIs|%k^vUZ5M(hzyB=wQESAvY`iBw|Fu4&GnAUQEJD89bMdV|--N$ow)lErM>(fV?KJ#cS~4AV@=n+zdCyKszA<jH_{Q+$-I9MY56-XOf{^cOk@LcKawhx?GxCewiOt!Mal1G2E2WEXnQ>iwQ{|rUqj$>rYx`m@=5@C-`h2xs#?@RCGaUTag>jBoalyE!+M~|3VW{8#FzSqG2mea8^l6NGC3UPFTVZ{&9?AJ@xs7{*sjv_7-@L;8By@a+gTMDjITy^|wZ^*nH^zKlRgrOxZGJe9Lh8aVn<{nm@)=S`D_#e6+Fy#7efA_7KmR}YTMEej(PuP;zs>{x(=V)2r#RNxoKYS9ciNA0v(iKCpJ~;wK7HQEytI_;3<rPd57LiqtQ*!XvLfm<_mh16Wlzj&b1~$*N8nzRHWK?b&ISJ9o_M|+qA>0+xiQ}x?s9L@lAAdAdfYMOm+FV}YtNfB(LM|09%3HR7whK#T72!?Wtp$#z&pI}6Q9BFcwEj+{dl~r&qx36DxB{xn&Z9^o{jpY>&dxkdAS1fD)Te^%Q3QU`kssUd38HWeEsQbnXi^u%)vJ@KE;0MH4W=F`v=r%I~42Fs3Z2<yzk-9st}v=J=NpV;m@px_muZT^Ww7@w@4=TNkSCXq1GA9%kvvKUyLQE@$>flDbzW5QSLd$f(=-Q5B~0avJSd;d)%)cC!@|+S+Wk+0z0t|^esJ3$~tSU@8X>5nS^}a!!3)d;kjSihjnQC=&;nS)&l2j|6Qmv|ALHbOPMRa`L7+QW4(d-9$tm>adQ;%2dtF!*B+k1dbWymsBiOIBy}uzB2Z^c6S;R;nrER-we|4Z+{b+*8@`bij`|(u;C;-E`?KZz68J$&G2a8JnK^y^%stGjathAJv5S%K+)(zX(c~fO^qhfl<2K8^Q6K*n&+*zM)M+~zbx!%A|0BVubGil2DVNFO8ym-=PFR54_w?Uipnv+trsJq{xfssn*`rYB<qYZH`dKBs7w?CnP6Z$FjU=o1=2m8her)D2^s~K>LqDcAN8s1&j&V;1VO*E}xCf5)hyP}-_#f^YM!{~}SEuCuX){V-pRDKr|KQS?ocrGv+y?&JGdTDCM`E25b@;iqg^RwfeIq5O-^mAkF1?37*ZQ$eHQY<zH^lqZ$QORs3DM}cFZT14rszMaJ^CN=0{744T3DZB=h4r&?U-+?>hRwb!n&RIz`bI7dH9u!;vO~99ru|<rLmrKPNL82>3A=)3nPEWQQQ;K?_j=eF6i^PyWC@q#YJVlMvvUccL_uObr+0V`c10T_Zleo5S!C6tV6$7@Owub$eC~b`Zw|Qzf8Dy)z3sf`a}5rAK-qt<r&r?&mHlNT;8Z({WtXa;5Pgovn1afdJW^A%Y>iM8vf~Q<d3-y|JN(HU+w(?>sc@Z;|_g=^(mJJea2rEUyJXE`~0paI4`m<!!HnxI&J>I`x3Sr{#iH4w-maB{BzOpFNA(6U+-&#{gAK{eu;Uquk;Cfu|Fp-g#RSJ+$Sw=xNqwb7WiLA$vxaKEkpjyS@7#llKZXc&RFcL``@jSe~&JHO6K2nGoItX=hBBY>uQ>;mws4$>(EE=y}Tt~d%jzI^QtxC+x8tsz9sdh^keuU|JY{njfBgnli@19+3ThFdZ#qhxqN%2^fzh=@&jU}j=9_b_)n(8*Plwht=F$B#LpZ9KXIPq8}rt}&l)Vg)}o}N?|v43xgVvDDRPwfHs}86r_W%?w{7nM|EFHa@7xT&-e|e>l^Kite9q!qPqbMke%n>>ld5AKDz9DYFfX^xm{;o_@N=z&Uoq%rN`S*((^g+<<{VH+(^TZwN@yd7<oHvXGS%mU{`)_rjc)i~{VA<MqXz%)pVF4vdzfjDVCo=pFu4zP2)PfrFLfljFL?k%@g(XrveE_QN#ro<VsaRHE_EeY=@Rl>@+^kp`3%M3)Q#k1dnDT91ViybYB)KZ`3D(_4^Sh?2gnK3b!4Uc$O+_Q48=zniuX{zBr9D=-b3C(olV|C-oQ{iff_=dKn|piAqSE_vqwMbXzCd9X!2z06tdEPkd=m#CzHogN0G;pKc|i$D;-GwoZOqCxEHlQxfi)7bq2X7If%NRY_Z2sdn}^{k%O4CjJk=ujJ%p^C9ft&*dvA-OSO_?$vddq$V%hMyQzDr@#MYaUDTcAUF10Gc5)nfD|It@D><4PMUEz~Whh=jT|-_$UPN6*UPPWpT}qxuo<j{L&mj+^_8|`=2T=Qx1IXQ}1IXRUJ?vqoj-w7BE1g7E8b%&Ro=TldRyvD3l|0@a!|gHH9uukK$>W(bkvg9|kv!cVUr?7*=aZF&la(ftmy`EXlgazZ$L(?09!d5%N<BnAN=~7EMNT1~q#h@qB&Sl7$*JTt>Irfh`4mI3K|M%TdVp+@zosUTl^!Fz+e00Jo(#pMs2aHxIS)g9oER?l$i-0XW{+~3I!-mMvOT=*QNtch8H#IDE0ZfTzcxd0V}|0I48<mDIdVCUX<{fYLv<mSAs1vQ&P{b9J8@pQ8S3LqEkSlBm!!IrOOidPb;wG+$R6Zc48;xX(VXf-^&<O_eW`WGzT_4R#SN+MWTl?uhU8`p#r3JB$o0wPsd>od$%Pn-^HQD2N^_C(lJhYXyHefAANGeULvdMZWpY_^MQROlMe-+9Z*p~NU8*;^E43Tdo7|1;Pi;!}Cx6ONtW#@~l{O~p<hBgOEvYrhEy;}-imOpgWTj=u)yS2o1<94jMHz|<P;--&I+F{K^HWQb^OH+cJ;+LHkxP>+FcjCLHXzp{H_`sy$4wZDTiK&CwIj7Txg)tf)rZ`k+=1##?m+HDZ9(ot?!r*qhT4#<v>CY#xgA4sYifORYqB4;JlT(2m0E~gm0X;mxG*&@S!q6UVR8|M;$rp)=;GvDBG-TVul>J27WqMy^FR9k^*bGZjmi0){`OiQf2j%Rl1KGr-yF_zU}mZ}P5URO)7R+'

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
