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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_013.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_013.stl', 'source_sha256': 'ea81a1355880e813cd9206abef35b81b3754c47b81e3aff6cf3e95448a0d1703', 'input_faces': 289, 'input_vertices': 242, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11800523102283478, -0.12906502187252045, -0.4999975860118866], [0.1180315837264061, 0.14708353579044342, 0.4999387264251709]]}
GEOMETRY_BASE85 = 'c$}r03shCb8ppSy=DSQ(in<<4MH3Z71Jv^P#4@~Kp<zBYDW;Za;4_PM;saD7GXeFQM?x~uB$2m|?ITMq>!xO<;3?~tsrW!R_`<vAoBzf$<L<7z?mcUL>;F4{=FFZw^UciOvj`jJQO{H1pLR-Q^)rq9+9(Q(ri!OBJ34melnK#s-C}0UtD`(XKKq!ua(F~&SY#b#wld#mVszYuSfAcDpT3iVe0*&_lcvYcjE#yJKRtG0H1mf<y%ra3_;Hh?W<(p`JN4+<!`Bwj+1K`#?SK3<Hkx2h>$Q82p^ogCdO!C4>ekbwY5wHfvkLdH?@Glv@@;7y$k(@(?PA{@m1|1r?`iGG*EaOer{7nHl)3v#!{f#5yXI;w`1a`LJL$WtlIl@Yuk2#JZEwUDx=zi-Gj!e5i{vXukLNIT)?6lEfA@L`mCrb~kIG&4qjoxy^T^lBe=FqWT~uCK-k*Hs_#vTwHEDG*)f3SvkM84U8~Cfp*LEB$qWWF+sQtF2q+<8>>s6)Hen(;yuP5rMy>z|GS9$*=_99>Tq;W3w_sv#RzqV*a5!KV@XX-blx-YLkp_1CIRR)spaM=W3KhhWdJdk|n0)C(N-a8$1of`d&m9N$O%6%=0`}W~9zRt=`)K2Z~Muk@WslI)?fVZ=yaKEOn%{{>Lr*fg_FLt0GCX=tnpWuFpigCQe$1(nE^7Y8b0`6Dx@rqwZ-_^ZcH@V-J=_{?;Z*spceSS0E&N`mkc|BKn`S~aE$!~ZV<9LgY*PQD#-VU#pyWQJk`r3fzJb&-p6#YXTc5?r^==V%1a?dx@m-A4Y^*Z;rWfV~VyL!+#s<WcGzv~jl-OJKfs{4?yPm88}(oU|~!|Sg&W96IeG=2Tn#9h36HE&N;{~XJ4j|wK=UUZt;sk_>jx%=9M4#j-_UMUsIBTuxd6M}E%iCVct^zU4!JaJx&hVM_ley}rL*Y0XuX5~9wUCFmcb>{h$UxIPD!N)!7QSz173&nhZuO&Pt`48n-jic$`v!0mcw?-E7>sImkrM4nptv^k7uV40+J2irDwqLI)7kp*&fovL|ntg(=-!9JP<$vSt*?M?0mH%_Oa9{eCedId}ytla5Bl~7Owye6JP&s|$4k547mu|Gm6D|D>@|CF`g*<QDmAU&`dUwhbXVt}0!EfOu<Vmf6_8{^kLG(}5P@Xuhje{RczCI@md2(Nwm9M*=;CYh%GWqt{H-&zX{o4LaAI+~D<`VkTp4NkWXTT!;Kl$eP>Zy%+znxx<@x5s2n|W*cdbx+V&ZOSRw8~F4^(y)HM{5eLeCMXVLVoHA5A%JZ!7A~(@a5~8zI<KNS1am@^CfXgGW#yCtFmvdtIj2z$=4&73H>AcW;<<*8zuAm3M=OI^L0$srYz(0=<{9f^*iDlk?-iaS}3nfN?J($7MvmUkLjzg@qJ15we{8cyq-$QFVExtHPQDf66TTVJ8mht?)jt6eK3yv6?sB?99Mm>?q>ZkRul3~_RV}V{d@K`$*=7n`1kZ1eB1V=Lcf{5)^UKPZ#&vv+y~(+o(C-NOB>%%n2)Bf=GF-7TW$HQ$(ZjA%B*~+tF!2*dt+U)3BKa}G}fi_r9yxH{s^s0_Nv2z?-+gv&pB@jzLxDl>!IUXq~PDPPPXY5+s|TrHUG2){Vei9^DiLZe*ec(dHAVc7FhXeMY)ilrmr13C*-H;>j(CU>wI{dW&Nz?%ZO3r%XwmtbS<|kZ~F2))gl9v={nMUm;KuL{?aJ&<$RWXvpq_a@=ShRaotm!)MQ$<Q)|+EBh@FZ&$3_pT+y@}`SSWN`{sPqnvNu2-bb8G$B{4ZN3w6`zrERP?teQ$$bZ?d-S13)Uu$7sHhp<tR-46he^)!~%U_Fr(Gl#+@q(|X{6zb*er-Jb#k}9-_p%3Kvgmurr2_YUmVI-)Y~C$%s6OdAO7_iuwt2V7;rS^(N6CI|Ucs01!Sv<ly4v!y?kjX}zwFE9<>xokm!IEk-rl^t^t@{GZp+&vJ+C^v1GwMzDd9O;_RZ&Hhj$>q?sxV1dqB;(GgkiH`nj*QxGX&X*Oq@tr}rtvb+uF|kNi=qzJlK;N6eoEf^X)J`TXzn9++d5KdR5bT&q0MeMXV5j{86uN8M)v`MNV-oWGr3A>XkoRGhz(uiUxK=WpjP$k!UYkU{OMymMxch3}|5N50}0mq+7~8BOnBwmY}@IQk{zxwps6Pt9*7`P#TmLOV_0o|q!8SMb%u`QpA{)>D!tzDN6)aKGYdyeIPW6Gy;wdY{xs#3E1p%G`bPeOYnc;NubyN51O)A>Qj>;qUdmZu0ll_D6;N(H1z2=grEFln;)oW4xZgCFCo~>o&Ugr|g^kX$xA({i)B;d4*oNf$FgbttVeTA25CSd_W7z=JO=;>}T%%payN@<xlsb`Q@nj!_u#v7eOWD-}8J0|DJOL_)2vXjLU_;@GIf(=l%9wS8*JJk8oc)CvgUy<kywXRqVl+c>QBCgmVKe_$K#<N8tJaf-j$wD7~8$TFpmi-?QXvV>Sx;;IN-6avyiK>NwvQ1|6gQM(^$`_Os;I?vI1c^8G2kzPKI^cJcB!2Qbgg?1OLe^N8vnh4D3g`FzYiWMB!Em(ByVkQDN@+aovd{Ne3%gsdgs-Yi5o-?I(fPrg2-3-bIFzu%$X@Oq^4L+4OeiB*59p^wwKs-EyHJ-?~9LU})g_95TiC6Ii_t&zO_VduH8ui*Vt{W71wVHMoRIjZf(HuyKmS60-l<Nj`bjuhsxoBSD57gBp~9OvgP;cdw`&vni9-xmHjFOPFwwdxywzu`XQ>zAkQ=JR(g{O;U8IFIJ9R?(Q}Nq7MH@;S2_9>{<1el8s*oVI(_S=FU!bK{B2h(?O1GAYXKsGXVYW2*I0`;?yl-BEi`@c(<%e%xroCq`^SFn%Ap68t_m78(a;`V2T0JQUgkJQVB?^#S{XJ3=1>cLcY9dV*VkTS6ZNw*)@|eG2>txG&TW?hEb*9R}_Peir&V_*w7_1mpLhE5Pr8Goc&7ncy#>hrmqFfDan+xe<lX0`L(dzA|DnG#k7byau`!{F4!<@Vis^4dZ_r@vRZxAsFvQFy0RR2)rG<0l_#4x)z)S&Vpuxv%rUqD1)9x97elNfxm)ggV&(03?qIw;$LVN({I4vf<J<0fHUx0#vdB7-iT$;<=|!DMMm^7;_pTTAQ*>1Ujm1LBM^+oKqJ9pz@wp4z@x!a5sVX|OTdZX#n46IMQA7Ec1CnI!iHen3ECUn2^<U^4h{x~LMMYm!LJ|~CmT^>M6nS^p<jcU?g1YK7a<tuL-WA-;C0Y{fY*WFg(icO(FVo|M!bW2XSx8q7;N_20`%)xjKO#W<8jc@;L#{M4#D_U=mIeN?Q5uSEO;7%@j~c3;8jL!H6j(k_*3X!@TcGd(C@)ae*_-@e*ygg`~`SFbRT#>cpEeaybYWNO$Voe=RoIz=YWSmL%>78-JyQq?qDzILtv)O!Cv522*z!o&A?2Xf|<4jw*hy9b_I6>4~7l`4+hVM&H~TE*vy8ef}@Ri&WMQ!#uE^XUq&#FGGdewF-E*-#PiVU&=~M^@EZumY+c*{U5aqPW16enT~`^iwRRVDCo~sa0^I@41@8c_hdRLP!ONjb!OOwsJYt-HV7w5T1YQW928{v7pkK^+!FVimq;hxeFgDjl#%%3m>(~=UJO&K_GYtbj1`dZtfFn>(ICK;^96SR0BG??W5eUXlLIc51f*(gPZm+P1HLgt%jJ=_OU~g~`g7FK`=fO;;gPBeOGgZM%qrgm`1HS<74}BWkAKVk#3)~a@H|WFQzk%<EHU{4hz7N5;fx_3NUlqO%F+B@r`V06+Fk6#66h4RRL7Rc=f$Kw?gX@FqD*RK&h=$O*;JPT&5W%=L^dWF-a2Kc_xC?jyGz2^VJP$e-%rqT554;+h16~dO47v~e8Tcgh2k;N*pOXm2zZr1_dKtm^67(1FC2%?PEVvwe5&A3mBKU$4e;RS#h;s^Gi`cw<6T$c`Bjy{S8Ib~g8_YBw9FMXo&?GR^EN}|=W9VV<$KYei-RHk!2*yt6AK*XGUMGU_&(QPWpTVWj3*Za5_fqKh;8O4j=w9#%unye{*1=n#tH4{pA3$e;KLF1}FdhgU1Re<Xg?0t|f;&Llf;)g8Fd}SNow}YLfAw!$cRw1NG{Qe|$-fj|LEV2DW7JjqLK-%#KAZc-#H&j$G<mEw%D({-68;b'

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
