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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_013.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_013.stl', 'source_sha256': '0598335f8ba12a24a3fc1d4846e1439f77036161c5663e83a309d9fc00c8c07f', 'input_faces': 416, 'input_vertices': 318, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4411555528640747, -0.26242074370384216, -0.39357930421829224], [0.44161632657051086, 0.4586634039878845, 0.39283502101898193]]}
GEOMETRY_BASE85 = 'c$}r133yG{+Q)ZPTY`upG^QOzf*4{<47Ck4R1sYBkYk9kB#4Niy180I4Hd+Ed(09MM7cybyGdj)Bq2#rst3K))lpl~;qsmJzW<f(v*ml9@A<ChS^fXc&pK=Gz1G@mud_W3?fX*MY6}1HQwHWJi$m)wiYOJ8YD#qY?5L>|!sj%f89CoW@g^_+$lTC>NWah#9!j*b(0^k1oC&l2JE;DhCI$Nks{WHAW=G8)H#00^_QY`Edyac|PPog@nKCXi-1Rx2bx?4i+PZO|`kwm#{Nw351^w%ew;Zmtw<|c`MV!-{Q?tZp<yu+t>b3kV;q|xsT@s&-*9YGu|I?#O<QE20ef_t`H#mFjqjvtRy5H=T-{G^5QEDsplh;lkIZD3w35Ubv^%VH#%N%r^(Idzkzowof->2mThsi5X;Zti|p!z$zTo>N?i$^+rJ`|SbFnRm0?2Wp;(kPDvlD9RENH?Fq^mggx`M>GBMn3jQy4(4~+cvP*oALQ8Q~Hxv2Kb$%dfMDVhshg#+1tIQ7P{3R(di(yW2vu)vA3bVcJfgX9rs8Yjh9k+)J3YlpbL2=Br%`bsrL$bqpd>T`EEo8)vxkarkkI^UVqvwliHtOOvg8N$EQ&Ju<e%}Ca>&cuU%bwnexCTt{-}=fZC~0kU{kq?J1!4m%U2$l*i*!&EEC_{Pmzz`rfx2**_h{eo@U`4wJV_-}9uMvcm}WBhuNIdH<Bd<kgYz5Bi;=^BgqfDz#tKhv)wTN4CT4KWDFvJdjQ2vo7ljwNokDp!!O22wi8(6!!ZXd`3PxIMM8N>F<Ajh}tPWLf$!VGy5fVsUM`*W8hDHcZTXW-OKGyn2}~at{%39+v&{nS^0igqS>o&!jFE!$A!0buaRzUN4p(M-X7VJy>Hi4vsY)q5Ax=5*|3_Ado+=K^HzLZc=Z_kwtPPB&E;G_^k3{3mE-G$w+)0(zQ))4$!zwAn(_QR)$P2)<kdv>+TbQMKE~0RTz~X-p8p>g@_GetAH!a2no8@I(s(?1<KU9B^m+Ne^Bg9xA7ZclekG5x7JD_XC(nc4H>iE-ZTalAdj_?yIl}n3heq+d3LQ!3FTE|1z4oXpr9NON`{j4JeLa@im)^dDy;f@hue(1FW}oyQ{{B%v?jLyD5%yZ&@_hWUetiDV{Br4YO6$)YChvsT0&DTSTjk5`M3$%H87sr-evsZdi@kH`h^tipYIUyf-Hq#~^ym8U&MNG+72U3KKUHC0XFiWdxg7c|y{#U5TT$v2`g_m3e5$|lNgm%n!|Aj1>PPI2jCW|AGXk^t?^g!#y7%gK`YgQ;?<`zPsra1WcCbF{-RkrD3$J5+c6$3<GuPLL^Ezx;>MJ((cGTCmMDg+04C4N(nZV-<udRhYzMlJO*$nm*SCQANHs$peUI~Xk{2H%kHq75sdyB}&#AP~6UWeDJE~fQd55C3qd)?vsah3Tw4zI%-EsMGSiSKji_=&~W>3DTtIp;8WUHXAVbl>PjH_00boo|p2$l?0%$|3gp=q=~y@72EC&Zzre@O<@7a+K!Nk`B}NeA}{b6nvBX?Z;IA1>bFb64n1Ti2c|V?3LeW-BZ>yAg@N|<Z`{*>1OYQSEiKZ=lO-2+z)qdySKA>DLq%!w#(d}3%XBx^0vOa+}3TSeFO4Z@8^8K1*asLy<PhK!|D8$13ui2hn>bl8F7i9@6wlHZ(KZnk^VlTGW%y|-PU<M$cx*b;*00PymMx+PGzsh_T+Kd=%js?`VZ`Ll5X&M!rP>;9mD<ntbpsUyu|Bv@m6jh-VU!fo67C`UE=y{`*Qu;p1l8*ejWV$$9&y|DeR*v@VYj>6Q2*fP5S&Vc%D2-W?%Uft)I&BvOK@x?cVHlzi)Z`-%R5AKi%bag2wXs!#ky)(u~eukKe`Z#BJksxL-BCkEGuW|L_mKkM_rL`{Sc?==0boJTKwx6WA-ieaYuDbO9f?XChz!!Si%qm-t@rJq~mG_aoUqm`VF!<;omxA6|XPUY|aS=XJa%`)BoO9nm)i&^}3e`*ZfrakXh5r-XR0Pan(syg$9UKD>IKy^&Lv>+k&~hkVZy+<ujg{9J&y_hRq7-JI96JqhIX`2lnv=_iYMorQNUV6R3#;&uJt9P-BGRs4DReO@0Ik7R%R4nGg354mFY+NbQ*kUsQ$(F4}gzE9U8c)vQto7P+9<Rab=Cg<?=6g+VAhV(P@`1-zCLF2ET`SNqVABuUr=0@?nDA4%%@gObB?3F_JB?<g{>xhHCXa6IgpLhME`S}iS`;)!WE{x~b)vdgLZ|KSE<jcR%?-A*>M)1Mu{Cnibh5UR-dyoC*orc5Yb$Bi410IK~W!T47y+!pKcpi0>=97|-Q2o8P>3j{ZZS2pbbA79S9816R^iQ&Re>CwDd#tPaJG;34*^ytGy|Q;Ht<#$PJ+&w4y4l<Cyw+#!=I0W;d|q4Y%jdNw>p$s7`y;jYWxihm@qGO#o%%`LI*0Gi#9w$mPtW9a;@Tyi4_j0CIXAiw?Q?Bs186-rhV8my_QpB(wkn%=pEIoydHd;IypO%yirayArod~yeE)8pa+<EcBkz0kh(SD`;0<`?ZU}$RKX{*8zfEq*zn`U-{noa@4Rd`(_M4@?>^GaNUpH(swc|aKkDIWF&j;RsH)>7f^BJnFr~Vu=jQc109QO~rK9s$!Wit2ApR+!s{yCJv-;bNl{R8hzWUrMU%>6SXVi$dmY0CZ6zKG{Nya8{-r}8@bJU2n4{peGg_eS}pd_M3>GJE~KXkItI_on%)_Uy;^ZL{^XK1grt#on;T@II|q{;@8l&0F{v<}LgS^A_GZZ}m~j{z>P5D4y31``f&3z}phxUu(tBvDuSoJ#cpS;_J=+n%7Tw?Jf4UrPsOtqIS@DIOBij`TwjF-&gSV1om2F1KJm84|kGR<EHcT$v2kwJ<@N6FSC&LEqcvd`fS~YOK;tWmw3xQTzcz1T>Ie*^7g~O^LjntIo;3F+mhfvyHD5c{PANRKkX>*YkR%SzeC{l?(p+|rhc{eZbQ#+=cn)Ux}5k8Jts>13HW;XwC_-dM$>hxb?@=-plb)|K9}Aued;{=-K~CDK;Ahom-l(0>B$b0S7YGY#3s}CfAgpB+tY9He!zHiz+v)E=~t{gK-Zc3E05peJbIs_-%O?XEWNI?*9Pq6=YQTax^CN}&b+Vl;pc($>bLMKAJTQ($140g$MPObdh2_zlKPhSVA5OPgE<TTAnzPqK>KYyZ#BL5liogtz0oy_(!RVsuh-3H@P7MnFM3}jy-oU!KJ>mwy)~1(ePdhR=WqLt_Mg%#o8TvX#QXL-73sW6-dh$nr+t$2^1Y?r%ZJ9n*j<&pt;&aIsb12SV`i^PKRSZnPozy}-~TDi8>L&BM6-AHgAWfpQL4|scG~O>=~peG>#$Fb=JVXOh4$0R4?XC9kzU`!-WV51^|iP5vbVekmfrdv*gjdK-<j&(?Put?yDP+-y>k!z$pa@#_3w{9W%hP>y>?d`H*G>C+J_lcBD2l?DZO2K^rup(I@izZmSXNV>Fv^^-=x>2N546jhLcxYHqJJWi}Z^0X#WL|_N`t+`+DFE@>=_2r_I+Ty&^rXOAYA2>)*`<S>}Fz!K0sF@aSjhRd@satY7w`=Z`ZoH`9E*(i_s_dSCFkUaOba>nsjuzxRVo^Yu!vOE2$>4|kHc=@<Du%H)TcX0ME0#qVSK56>`r=NR~@i*nrj83*tGEbTa(d_vwRY?5a7c6j|>{6#naIE?F$uXw&RuMf%2cJqY;d4JP1Cf)3Hczw<23ubQ|oyF^Q_Y;O&eRyqEoy%_R?>NivNh?lsJAWNsKQztl{PkFVPoVw2-K`z1+Dq&U+PNQh3%@7OpS3F0Yu!EFj;p~NQ5P<j=9Rop+>WdG7O@{u&aE9K!6T=%>oVfmTdzxr>z7?xzZskQWtY}(>g*X=rHzXMZygus;IPcn#@&Foj=NG@%`9zR8MWA3=as(d`T5f3r#3f{{@q2l%yU(G%RE<GHpwuzqt5DntF-$_dh2~8z4bmS@s|5Vdh7iny>&iIZ=KI2-ZDR>x6aR!`j+`wQr|M)O0L&3PfE_yGEYkCTgI`ZzGWOsj%yh&>8;~c;?3g~>h`bE3E5s%74gwk%DetEX`Jbwq7_*WS^7UkPi^ym`lskNLGAwAe~ONCox?^~*@oN#-Ui-*+z#FW-iq7|-U{A?+yLGLUWZ%@UI$){{0O`nyb?w53KYT1Py{bVt_3d!FG6kri;M;@0?$Md{4R1f_+9Ws<W%rP@C@V}@C<MSavnGWJRkWUSmZ+ReDGZ460pc_;JM&7$Y5|Aa0g^3u*f&T9l(Lemf%2eV`Ou1W3WH63D_STfNTa105?Su+yXfYEOHpQ1-LVEFt{_gBXR&(<Xhm5;O;1b`yhLP`+x@`2Y?5Hhad-ohk!>Qhk-|c#~??6$AHHp!@%RgW09l5W5FYl!@(oLLy><24+RfGhJpuy-$wQZzYXqz><Jbb3>Mi9EOH6B2l(&Eg<z5IgGGJ-7P$)icd%?{70yNE8q>M0!MTh4*mNx)<61?=nXWy~)IV|PKatzOB6pbjc896|cVK)(ZUu|nWE#6ort#f`@fW!cEONE-*W3_15V=zMYc2^EbFDjaDRL!P<O;CJW#FaY1<1wV1>hLuBCyDr;23Zuir{I;cfr%Z;mC>LaPR~a!IO|Pz>~n!krCkO;91D|V3BjdBHMsxfm<OvfJFv^TY(!P8-p8x8zB9`4Z!tL1iyg{0KWllh-?aO2o6FK9D-~C7TFmb0&b7&2=0jSZjU0kD~ezpxfHw<<Eo<wjzY$OV=$Ic$RKbOxHU2a9D-xFMs@{v#W4g|ag~0qQW-^XUlhSRk)MEff)kL5V3Dcd1aJz9;7nvTI1~H@@)r1}t9<DyS+3&R0V(ge%4;Zs`=bc9BmV&wc?fI=A4Z-59|oUA5uAg}0%zeIa?rP}(O+U4_PVQ7RrpUCSMhL_U9PgnRd%~dO;>5>Dn2NJ{gBJSe&8v{ec&nJ1IT0G1K{Jxe}a#LPa{7Ap9Y^tUIw2B=OM3w^T0Qd{{r6te}()G{1x~P@(1u8@IB=B;CtY^$Zx@S!A|7YU?=!C@^kQQ@O9)R@O5x5(g5dzGmt028Q@dMqu^8EWaM6OGI&4oL-2m^WMo_LWUz{?0an4)k*|WQgUcgd2A2m{LcRp91g?NA3$6gJh<pWH5$uI52lfJcB5Q(0`hY#b8j9d?NI&p6a4d2PI2Ig_JOGXdA3+`m9|500o(7))JCNtW4sbd$51bCZh`a&52)=^+3Va1zfV=}P02d+efs4R}$h+V|@KvM}d=;FJybaC=UqD_5UjU~ebHQogbI1(vIq;{*Q{Yd*Nyuby68Io;KlmVcJ#sR5J=lg+!8ULgWOZ;CurIPa*cV(ESqWShTpL*dTpL^mSrJ?ZTo365t_QA#^aP94z%^Y9_Uo?F7O8^Ug4?4A4nZ~ohk!dG8-qK7J0qKdJA*qRn}9okJ0ShR9l*gzKX5R(9kMpK9k?~J23TY@aBFZY6u~W#Uf`DC=Ew@*=HNgS!R1}0BGMaK0qhNa4e14b4eW!g2KE8hLe>D+GI0%DoAiR~A^pJhz;7V^!Eb;YBAb94f&-9E!2#d~$j0CX;QGi$;QHXYNEKWc?2CLI><g}gtO>3Iu8yn<t`4q(tOTwCu8i~qR|Z!^@x=I)2g`93+zdr<3uGm53vdv!D!3}nF9=0&8)RGX1J^zFZ&&#hMerXef;~JqAA?1mKNbGo1Mnkc84u=1;GdDNfJG7f6j=@|ir{C+m%*Y4E=GEQMT+wgeBV{Rag|?C1pkI2_&M@Nu&DDpzIPw|5Ggi?5Aj*>Psp-hQ3O9hz6usa@PCjmfkXRxl&SX8|MtJK{Pjoo5dSs*k1f`3y1#Zbe{-#?t&*3Jp?zN#`vuoVw+#JI%MriCl>Y%mhSJs'

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
