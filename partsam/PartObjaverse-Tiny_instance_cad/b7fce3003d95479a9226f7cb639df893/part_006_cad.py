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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_006.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_006.stl', 'source_sha256': 'fd9af7a78fd4ef4ce9bd8309ca8172b426ca5cd1717d67fbcc1fbb0e0f443ff6', 'input_faces': 580, 'input_vertices': 344, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2451636642217636, -0.25797101855278015, -0.4607906937599182], [0.25024765729904175, 0.12758326530456543, -0.2252557873725891]]}
GEOMETRY_BASE85 = 'c$}r133v_H-^VAh7OgF<U9VaaN))jd*RB#08c|wp(xP-BMHRK&S9euyQ~gtG(5S5yK~TX(g4kn8V!u^tt<p^w<(+fpGt-%K=Y5{{dEa<`&-Zh`_ji8hH)qb=WfF1GMT&-L#!oG+%4fI7`aPN^qKp=%jU6&-%<vb6jE)?UJU&D#Cw=i_>Sw+C^@<x1qK(zw3?DpX^b4cH+jznsAKEIsp(lLk$WdcPC5?D)<fy?zgx@XcmC-|VfAp}V<RSXwh-Ohy4L!~3H}p*M{2zZx=`94_NjkJmSKq1YYlLdYiso-~@dMo^AGQ0MHt6LJF8QW!=BNHAX}|OfQa0J^tG=3V&YM^|wZP5ymHj@?QHOceeA5rg-y5>1gIhoNW<TB#ZMXFIEl!u(==Xd#-;+80h{N|C?B2mGAK%RPq@3O5wmzzF_G9|$`l!BnyjC4$eN;avUs)g3H~aBxFYa<%AJsRH*Ya1j`C9h5Z$!SE?|&!ES^xb(lU(!hgYuR2SADY|ZEMGDw|-RLtZ(^BKdNu_^F&j>^xukJC3WD8LO0)gd04)ipV<CEXPudyjXI^u<T-rLj}u+%;0M)d@LhTbw|+bq4WIgfoW@)2{rEnrcEZh1&7XYO;V-_ix`SIjzM1cP>8Ed{_N=^K_J96vp552ZWUQ0*|5;Pu@UI_VC+n}h>C7L{cD>x62baiv@4}hJb@lL?4ff*=@;P2@*NTl&6DF*;_pkb9|DJxEGo_yzzr?;is&Aeb)i=+J>YMeo)A!`MXyrzw$bK&VBK!AszHRtV)tM@MZ>Q7JPrMp1d~Lu$S+~wNC*}F=Q)u{s1CvF*zxYP!`^wBT{3G|J*!x#~vwzh$`&WJI{H}{x@3wzb->R?pR(-{{>gS}amB$wokgu<a+kY!?^8>H8JZkrSX<O3W@=f2$|L)zjZr7LUTh~|N@C^AlbDZoi@&3d@yYJgJ|De>|QpX(rrKQIE&$%Z~JN$bkjQ%ej&9nRd+Q#dRclM++c3*p=%ND7NN;vw_raUG0dunF4Q;zzttd`eTVAL(+b))M;M!tVzlKp(CzP0`xs;@BCVOX;LdQpAr^<mAvMaDkdI#&3J)ACOmkJAi4x%o%3PI{r?UyC*TKQ?_Le9xD6js5>}>s0B_t}##g1OGABx#b57js5QlbM&wH*7bX)$Xxk+-dA#+Q=@krv-{fF<;FUHXT1KHzOQR}<MqDRy*x*qJ{7mi<9y+Uv(AQwS#sQ;XB>63cmI~JTb?109&z{!?#c6_O{{uc`fsPraoazZuk0VoSN4zTtNX|F)%|1n%KowHtNSN(n)Cy+ryBdef0A)th76wNcAcuedEJ@5dY!7ib)7Ez`(xw$uAgo{@2YR@+wnI)lD_)7r1;kBaNLJerKUGpWY1T9EB|ckSEW`cHdFQ;x5?PgpC-L7_Nz8(SDIYM5vvW~KWCiu!xqT-QyXkB{J9ZRq@UP)hV)Nfkn5@K`t3dGuh}T;BqnDVujjL_ek%RP=BF9^;i{3JzW6igcS(6m=FbQi*HP}ZFQk8Kg^?eA#dv=_KXHk?4qqEB&x`+$*G}4f@0B?Dc`7jY)l;s1&9Nu!zQ3?^wp+gCEBU^-D?1$XZa87&x4t8Nt%2u+-S@3IVO)2gS3BwI$JQxy_?_x+bImt>C10CxKFdC@Km3f*Pe#N6c^>P<=i7bn*^vFld3mzH%@3T4KW_JZ&DZ6+<(s~mue~#Uk7M3Fw~YMh5ytDlm|7?7zBjAHK3ON+I9}EF^bId`_|<pqam~jM%8yCgZJ*bdHD;;X{xN-Z{{;E$2h&&gPmr(VtNX|IY2H$|{bTy-{t5Eg50<a&pCDh!SND(B_uNvq{bTy-{!x8%KbXF{e^g)1SND&v=?_cY_K)eS`$zT7{b2dZ{!#s)d}aT5&$n42*JtRxUH0>6`dZ&g#`n2tZBM!Rz89A{>S)Pbvt9G?gYusqw9`JXKYXtAy^Y^@>>tZ-zfkTI@8&D6zJGQ?q22c-&)epfZ~AJ!_VL~=j(vN1nc+XXexKuf;d|>I+-t9|`u>Ik3LXC1dwX2-@zs3agvxsy=WBVU(a+6{{q}uj`5*6+efl<e3fz2u%6rG{zJJ+`T(^AFSMz<{Lv!u(`Xdgkl>L{!oZ~o;rr+X2>3jR{aQ7S5a`;+Oq-!1jhk4m<bu3@0<IfzE?Wprl{Z-OGn!Meyukd|$jn9+5_mkcIL5B+MzE*#O->r@|Zh+sdj^(R$y8XG$vEO<}8S{R-aIa&(nf}F2()SI1&DBqRFt5<=d$0eH>sCjrG%eSyj_Ip)w3?BQI$C0kF>jAq`|SI{^u4oMOF#8snyc@d6zcH(_nq47R>wDS;$F8prmxoV{ZzwQXHOM*|3dxzsruIENz+&FODKL&zH;9q$mhO?cV$iE@#U(sg(g1pQK6gfJy6$~ADWgS)HAY@)6cEHR_5QG?5y*1xlEyfJ6E0g+BoTZLcc6<_zN0slKESA%kMi{#=(u!zj^y}nV(hSgqxpuedS??zofP7$M?xRr{D3g(P!cxg$}>!S~<Tb>2iUqUvEjC!#|z#t*pN@$M{~~_N44vi^`VYTm7ToDs=O;)lH2$7i#Q~k9%Z&VqZ7aH}ez6#z^1SB}LvBN$oYL(9I7VpJCiL$eeG~DS1<_kN4$O#`p2*s~x`9wxnFo#HizrI{s?s3f+9~-EzkF%9vBq_x`od_<lDpC*Rfo;l-nNUu(Htz8)rCd!f+PFSgfFU(3Ik?wW7<<oj~o+9~@~?<?X5-B&by^}eF%tM?TT49J##@)YCy<&<;#9lqw3-{*Xh$BoZ%-rG5@`BgXNx~*G~&$^kux^6)}>tOlHx&`^<`?t>DEB&|I$$g!e-MGNjKQ-`(!%ti!_qDIz-}!F7x97*s{7Vhw_2U2Z$>VN*;Qp4!9R7w3!;j5z`a5TAcCCXSR42M}mc5QI{=@yU@1!cmKH)x(>TA~`j@W(ubIwfpeDy;GZhoNr`8<a|t(ScN4>Zbm`YE-I_lH(HoplzhHtxf}@riTZ3wNcTI62grUt_fKI`(a@alHTZJK%aARo^_1rmvny#kbC*>8tCn_}2R4`_7m3yXBj{ny)R5_dCwloVC(d@7I~WdcV%})%$f;9p!$VRY$pBXZgzgI?Gq?*9EGC9Clm(AfNTOd}aMr-&}voSFR(~H`mkhmFvjzmGh|jL3Nbt$n@3otNKB8l=JI<ps0~=zOT(O-gi{ryReO`@0+<I&&~HtD(~>M9>2_zeQq+|?^NG>KUMv}zy#Mi+EwHI)bii`Oa7iqD>1>DUwNXuego%gIO{8)Pb~lWe#UkEYn>wwf9g6T|AUtb9KP~-#`1F?F+O+kIm+^t&pAOppK~nV{y8Vk@z)RS`mbr7UQN?P+^2<ULz8TO`XEg4W2*a~J`9igU;XJr^Hz`jfB*F1fe=l*UyrhS)X<}m9+e5fkLuAD^`ed7j(SAu@i-y4p&nJxnrI~akRDZS^{X;xCB{@kYr@sw>gdDp!;GtrR)s~Mt?5x{eYi6E5LzF8oc`Jnf*aV5p#fS67Ck)1{6d@9dJ)<fZ31`Iqmv$;iB7CrYkF;mdf|3(2ecC`dTVc6=k~09d!Fxzc7i*?UC^#@4f<+?c7{7MUn7pI3&+rfu}#p<aA(FhVXiKm<1UPkBpzeUYU}&_5j|?4)otwIvCyhEuEk@a)ofgw$F-?Z4He@aCIr_+tHL$m%4jvXGF-)0s|xxs?4j3MXl+<LcRw|Rma)|=!<<4Nu=Vf&b%mC-^<0*EWvL~&nI28_Xo@}t-xp$VDYOYJLU0+h87x9@X|yRU!mQVn`hqLyQBIFyXc4%)9u@T{iWY~9!bOPU<QIcWpe5mQ%u$}GK)s6agJ>9Bo;k{)MQk;Skynh`=9rSyE6Ln~kLkyERF6DD@L@vm5kl~BLU2BM49<tYB?NCo^Wcr}2J|qz0p5fjfj7aM(c|!DI19~(^O-w~5WHBA_w|^jM=H7)UQA9Zx)FYlF$>XDIF+1*=mz)$#w<b?!VAe+gl>XAWXuwD5xj_;CFo{&I%B>>m%vNN`4Y{7vpBXdiN(~I4vRH7pvQha_7Z|~3Bmga!3PP!htLD?A$T1jI0M}aXTWRFTzCz<7TpK0h1a78;q`DPdI&zm+?j;nd3sFM<83|Wp!48)<jg@c;QwOG7w8;#4mn?-Yv8vSGZ*~={(_vj=vw$4#>_|O!gI-)kFJN`Wy}I}K0KeC1!yLm$+0aU=27EaSggS*Jx=OTNC++<1fL)TpC$yKK~KSFU_T*vD_RI|g}0yu@D_L*dIH`CZ%0qV+u<GP8Tbry?;r$!qsL4={-eh#^c(maa#o>R;m;Ve5?uwaB4;JK1^%2dU!yDGmE?SlZi8nrW;OaX{53hN(e3bT#-yXG;nn1%qdVXo99uf^4K-%NVhzsg@tq#$2*GCw!2v?>_k`dJ=y~`8yo(T=jh=(E;hpGNcqg2L2H+fcH~Kxi8{UInfG;rj9zyUkJ!a_fi5^SQW$-d`mZI74M~q2Bm%>ZQNkezSA2a4FG!0H8=PNV^{**Dx(XZgI$XSl=hEo``0$mO-Cuaq^2j0W6tss_BBLx;~FkFup^>`H>0l$O}Lr1{FdHk{-@p|;tqaPXv3+)XHjfI~?`=GI~Io~VPeU;oN;eO~Va6dR6eF=_-`=Z0(zHl5djJ}3(T)oj3;ofj8J@lckm*L@PEF4R|V4oh7^_YZCfZOZQPLB@g<8XU)Ao?^c#*Js}B=}8qAUu%#H<@c9<0io4sXvf8+riJE<Kgk-KSK|XQ&;F9_-Xh}bPD_?Z1y>YHHg-uryftBJ>b{$7^TNZG#O6j`H^T3cqIH9+S67ensL#L5iEX+>rqsXP(8%|Qz)rN5l!4!&_BQHQB02#dW7JI!l8^8T%NpgXi>NV^~2DT@I%a12`vpj$h;NN5^x3T6-SH04^giaS`sc!Zza)C_(A5m4=oLsBBwN3#P(bf`Y6J&mf(0Ra;z2ciZNGF@`~bx&}SujG><b3tq6xH$6A4TD&Px#LN6AoM-M`9Ekdvdy{j24^dDGg2st7IcSpOyB1eq*8@&U2c>WPI8h!+>i^jrr;c$AZZR=TZ3|a?{fqSF%;NEZ_LU2490Y@-TJR!I*8Vh&l7^Bgia5Nl?J_*Oded$^B_XHuh7up-{1;?R%;5aw|jfWH9{)FIuXkWN5JqZ4j^Y9mX2fn4pO+9`>Z@@pnKN5nkqt{?@-Zj>v8{Cu7m|N)2n!!SUgN6PMixAuo{R0*u*gQtT3FvJ&lr_D_-tGnWV(kQr5d4c~gy3J%1X!r3`78VVZ;nrdV2xuD{4>x03I7aVW6z78?x6Qr>pS%E7y1kQ3v2lodJVotO_Oif=DNW;{s#Y!-h_XL|3GiS*O~7}^jG*-*3&%Kw>kf}8TS)<3y$FW2`B1tz1HK}tBckS`S)5DEUtAAS_`cWkJan`pvO4$GCU3*gSLdnz|Rqa2cV7N0dRjpaA!hrTeJ}@v^)H|9&hMzkq~?d9SvWCTcFRvLZ5<Lz>#PIEYu4NZ3Rcd4bd*}6+N!n=DkW^S6P>f=nrr=J?iPv2CWabfjgnSU@>kiW5;s*f}69ZSJBIGS3O$mQI`-Lfp&z2#=xS7aOM>HC|n<oKpVgja9y+xe3i9mjz+;T97_aRA8t<FmS|%*it#PbOK?5bE}RhD2<;9>(NlBuQQJJ>%n?p*WAa;&+k$i4fQaPSB00}>m`BXl7HtE!g*&62;7%N~xwi%P=RA(%T)qy!fsTRSfJYO8pGBX8pM{@72f$Ck321+~KRqO%F>nIxMLWV?xE0zOZUuKiyTWx@r><y2xFOFAPSoRhJzmgbC^`gv9&V<;?ljk<DIqwD5Zsaw+=>v~0&NCIk@q~c1rI@6!6F0?MO(lk1P^Ac=-cc;a8oo%`?t>|dKWqv9!wp<anT{6VMYF@|LXkjk59a(IsW6bI@0-TLi@<OdM)dhhH=rw<mcs3{h#=<a7BER(f%78V-&m'

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
