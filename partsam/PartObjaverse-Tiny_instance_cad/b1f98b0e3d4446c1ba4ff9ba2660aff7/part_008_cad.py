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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_008.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_008.stl', 'source_sha256': '5ae95156237817c0dc1637ad83675345733713535e94bff79fd4bd9e61c59158', 'input_faces': 677, 'input_vertices': 390, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19036903977394104, -0.3263363838195801, 0.3171580135822296], [0.09828808903694153, -0.03767925500869751, 0.37493371963500977]]}
GEOMETRY_BASE85 = 'c$}r233L=yzK1L9tAGRqL1@;nhJ6WZg9wBK2>TuqL&9o+1Z0t=0hvJ^mjOnQ86kkOiHIR=D$o#i5!pdph@*}(JZ5xeT*o*1a;v}pebxW;JLjGEIOm@4>z_BbtE=v<x^=6LNeRVEL_48>^&J1vt!*kdavW1CIML4I=~;88rln`cX3km=<y3Za^G~>D(1?LaW1^hLohM=@rDvyQ#dPt-bj#=*)4~^%F*9pUR%+(NnOT$4P2M+kMs|8(o;@XXR(j#*Chg){xA3)V+QPTk_ka9Xu5c6l#goq-D`d{pgfoUta_1X83lUgT+|2_M{&YT4F7^HX^<lZQ@6CK~{eqNTZoQO}*Ux+FOCBtjpYP3m%f3DB{{5s07rpIBF5l~mUUWTD9^C#-SbhJ@xL{a2fi0o-^SWFN`(DX|o6d)|L+-2keSX;Ys$ADksXIRCZQs9m=PCDd!PWP?^(7CsIvMn~uXCxNGozQA`&OR0<o#We+v8F)=6a+&cp(0!H+NQ7dMoVs-v0Ka+y2o#m%@%OdBL)T^WOG#F6~R6^IYP|NcAPx^_?bj-|~KMaAUPl{qt#;y!%1&z~&b3dE3{yv@dx<=Jex{>PxQc`@YM0+k0GeF5BaL|IG<^JDbN|@$OHXv;T84KDrhuPiepQrZ*4Ho|ors$Nx;8n>*iCyb{*0Bu}_?&fC7urG3d$P8~ZLslMd8zCZqlJn#29TXu!oKY8ta@BY-e>`%#4*8l2Ar23LeegBDX-QyAX?VihF<AvPcB;i8X_N&}(KY78fgcFhKORnqtQnL?)jYpN+?dgBq9iJ(~qc3}Zm(K0)B6s#bdogT#RBpG2JTR_YFj9TVb$$Q)pB##`J(AmgzB4A&PR8)7-u@=JJ)gANbS+XIoPIg19e>3mZ+P3u>2&Xy+y2Y3SH1m5a{s`@bKdrKF74YqKjBow`sBKPVAtHe-tP@e4IXv(*V3a`yvI@UKyuu>-u87a?Mv?DCg(@0FS)KCtlu%$+plzPx2HmHH}|*ebIE($buPzUa^JAJ??kFEx$P%sZo8lTQDv`$^%IrbeoO9@ao+R(UY*PDwe6Hye>_rs$#wmlS{3$3+8)Vmzul4emUn!~@71~dUdd&A+5W6@+n>p0eChg<>-sXj^!7+@&-1149d`eIR_rzJc#+)B$F9u27BRp3b67ipGhglq8^7DOxw-%A64$)_Uvg*h?z7(Zi{!L#+ZlQHRHXVgSM>wOI`8s+uj72+{{Di@Rad?J+~!~XaxU!m>Rf&=dEm1bPe!V5b5-AYxAq?IxYN0vS1fz_pnIG+KiGMK%56U+m-B<&KRTEFLoVkBUEk)azMLQQ_So}=jMKqwLhZ<PS;n2p?YJYi*JU}cK7Ym?Z*u*W{;YH9&yvgaSAJKKoZlt6Tz_?ao2&YA{ngtexgGC6ZQbYAW8P@TugdNCC6{@lJuW(z<3cX;MqOX#hw{AzKmOZ2PR_#pVdGtLJ3l-;BD{W9-Ya3_I{w2@{eo5D<C;7r-Z|@SM{?)Py3>*JK)0IP+<fe<>ydIhevi!x^*_!hcKnjdc|+Q_^*KN2T+R=6JgVH@@AN+Vrkl(BLGEi*ZtrWzW&R-FYjfraI=Ax#-9EX!PpQ);)DHJ?a@>pL^b^VDKF*%6u7B#bEAx4KU!Zb(y^vhy`LaLB?R;M4GH=)IOK!(Y?izRAX7BrCyr|rc7jn7pv;B%(?(cMN@9${e$%=m6&AA`9`$y+;K9`*Pbo+bB<$he}az8HZ`?sdK{Y=&+q`u^`E+M(E;S1Z{zt8<+*!Z<M<Jzt#kjwSmt`CsQd|UdP&ZWOeF87sk9Ca?oQF2)yko~N4IgWPwWxa*{QzU2q+wEjsNbeuJJ~JdSydBnsbbY%%qraDR3BCPtU#$0o<a$5I{fOSrlI#5}^C-K{qjG&5<@_w?Po3-j;N%Y2>g_)TFCBj+Qa_Yj_rsJM<+nr{FGX^Wm(A69kz9`#$@O>%L^s&v)>r2To!k2za(#Y~T%R8#*XIYF+x8phZ*X&U{?xg>KayOXKPA`aPs#Q9Q|Gq*>Wf}-bA4UVxm*{>^>raIv*|jwzp3k;&h7PxTwm{OuC8~s9d*6axwK!fcJW%bp1ST!uCM#HzPj#9uCMz#m-bVJe!SZKdo|CIT+eeP*Yh07^*l%Cc70&=&`>*So+i1Tr`h^?o>pz{^KLyo|5UlXo{|@tf9hQ3pX5d6pX7S}sdM>WC;q8LZu@GUuX8&OA=mT#BDq|z$@M&6ay_5dx&7XchK+XrUftK|-2N_deP5$<TR#xzb8~gyr*pfWNv`kvisZ5%$n|}n<of<j=k|MRX3TNNjlPeTT;E5N7r9?1FLGb3a@&4%UcgYVCrGZ>6Ks98ZXmggcNvd5x9wNIv)t{!dYy#4$T|tRUJr4GTw3Xld$nGqbKBp@^?H%cZT}(H>qR=(_4Rs@&h7POtM7MiuGZ^xZm$dEdc98P_IfJqsP#IX>-u`VPUm)e4jtLxwxicGRc?PTd6D%@mD}Uh^57rb<EYkkCD-e^I=9D#T(9fuT-Vp@x;nS(x^4I6xK!)mlI!(wo!k8{xmpj`xvnqQcNup&x7(AvWV1{4TtIUDTtMgcd&%{4fxzc?wtB~%?LR8F{fAsXH_^H6KjiwkiOzL>{oF+7cAYJFV2AtP_46t6BG0E(Zr9<-i#(rFxvpR2`IO3Se@j^Tn!A70b2^>d{Y<W()9Kt^kG|d=YDYbnw7GgNsdGDi$@Ozdo$LB`elFJ$mD}yvv}d>5KlSrj$@TMDmD}$n*Ux8jHm=|6Qaz`ZTtBDQxm~{^*UzbSuIuaP)H=88+ttV9y19D3FS&lcuXDTZO|GBs>s;5D`#8JasB-&$NSCie+o|4jkX*m#pmTfwLayI)@Qn}dbNh*UA478eK8DWi_)5*)@3ybrC$YJDpG0!~-iYLK-)+y&D!0e$<FN<a_SJhblI!<jB-ii5_#2!!=(exk&yifepA%R$=a5VNUJ!Ya_kzgvdqIIIO%HqPyLnRB+f)Z`*G}!`a~xC3I?+x>s^?WI6Pka*$gfgOZU4V|m8xT>PXFImsU9fYhSG(lDy)E4#cRUKcul-6tcTadTfvTaE4&9BjQ7CD!8!Oid=bU?2KYPN@I8D3{x19me;5A>J{T49ukdP7A@;<p;ho_GyfZ!&&cuh}Q{WT0;p6xed?d`kN8<4m<4N!_JP98Mv+!|v3Y?Co;A7w<d<;Ga4#x-K{oo^bKfD!;!CT>VVR^hR?!Z4eA$RbPoe<x`KgQpIf56|tUxkn3uj0$#2z(hn0d~eG;6q?bd<fnJK7@C{+rkI%ws;d*6>ow!gf;Pocr#cRZ-%#rt?>4EH`oL3h7W_|@L_lwT!g3Lzor<^fgA7*jE5YG@pJGi{2YE4n(=U#&&De=Mmpn_@s@BX-V#rMQ}8MD`vi*dHZUG<gEycUZw{02=6FXq4)2I}hbee>yf++!_r|-zL3mfZJ?w|K$D6`dcvHL{tc%yfOG5`QjsM6vG2`J!it(H99sDMK6uycd#b1NV@YnFC-~{|Bd<h(aFTp3mF8D-z6l{x+!V_Q<JOO_MHpCynd%<RSFT5XYkN3j|!fyCLd<-0hkHJ%68lH*=;IHuj{v5^lPMCw|FdlYNjGuvb@iX|R(2R#q`E0x-W27Zs5^n?(@C5pOBZ~2|umN5c|F;t=#!HYj$4lUqU`M<X9u2$W(RfYR8?T8!1iRu7;Wc1;yarwsHpQ#r6=6NRB3=xZ#*5)UIU$<y@Ds)OXYeNe8GZ#G#joH&_!=I>_rj;}z4#Wm1mA)`11I9o;49!Ld<8xqCgAh&S@02j7CsI3!l&UGupgd*&wvB*8F&^PgJ<CjVJf~5UkL;FO8i;)9R4i+3dQ&va3{W#@$d%4_-Xhlej5J}n(^=<pN;<v8{v)U_r^^z{slB+;0ucJ>lEX+p&1Xi`E0xZR>Dm&{udaHn_~QLuqJMb@qfaHa8rzb4{PA282<;Xiko8mudpI+it#_gVz?>B??5vi?of<>06)V&z^}n8_%-|z4C0sY6L2qn0^bj};QR4h_za$lzYbU6ujAX{e0)2;5zfLl;_Klwd_BGfX5ee^7vK#11$-^c!q?(2!G-us_$Ig#--Pdg&*D4qJ@6HL55A9LJP*Es8=l7V@Kf+Z{1koz{)`)bf#1L{!|V8EJRjc14GVC?zu<;{!wvt58-9-){sTAsD{lB_-0%)=_yKNs4L7`m8=k-o_v41SxZ&%#;db0`BW}1JH(Y}ozJMF9#n*DY^Wi3Z6UQ|l?!otPEb}SG55PP;k7IU#V*Dh$f#2ZRoP_!K`-SD(!tw*G6&3Oy@H$Z;`tdq=ADE2y!5@XQ@JI1Ea1lNSUkaDuOYtY+3j9fYB@Eyz@#Sznz8qf+r{Rn7*>E&I8=nZf;1ls)@BzFRUK{@133+Y&J14|L_;>h0xEeo*KM$wk&*SN^51x+uVGQoa8^G##1N?qi4!<8S1xw(i@WP+r{xd8FOW?)uG8E(GVL7}!UI|vmE8(?a3|<>=1N-1@@BwftJ^-HySK~ABb?^|r4nGY4jvvPFL31qc@!9zO9N#YZ{dhY#8gGXWgwybWcp99Kr{Qy90H2F5fGh9?_!77bUxF`$i|~c`JU9!Vhfjsc_*8rt^y9<uI9Lmh!>dDc?x@aZ<6l#ZUxe@DhQGxx;xED}_=|WZd>GHf<6&bw9&Z7w;Vtl5uq<8+zYiA2@54(%2Y2ZAB`L-$!ZLV8{6UKGXjmSP#%sVzcn!P`tc};fV__RS7LS7i@Hl)VoQaRb=fQROJp5&N7=Iam8{Wg;#=nGSJbcM#;}sYq?eGeC6F3lWg7<}Kcwc-3oQsdZ)8PU<9iIW0;4|=SxDe0AGvPcu6Q2yH;*;@Fa2P%cPlR!JA|4B?<FR-ZXvRhrJ{$iJit!8ZB7TwaaDig{_b?OxJw6x4<8$#O*aA<&JHc9bC%itq53i3`fhF;h^!q9l<39Kx?!!A!j5mkTcyqiFtbsSeo5DJHQ@kCF#oOUsVI1BS9|}j}L-Axd4^PII!<X^p_%`@9z70PDzr>H=pFlGnKH;<RD8@(=JPP;0zPJx>4M*Uu@%}I!?~f0LGw{LqSeT8E#ZzG>o{Eo$lkxHR5I71Sf)9X+_yD{ujK$mHjbRnMF<uIqu~CZ8#{Wn$ejZ-HFEAd?Q;cthbMejiVwi+4#>c}>_;|c0tdIA^Tf-`N75aT^it+BS1Ku4UOEEqOHpd6y{b3`#Ki(TQ#e3s@VLQApo(Q|*iTG$Z6d#SJz+^lHUkaDwOYx`SHvDOPH#~yx#*e{I@MHKbXvV`WJ{$iR^x>u$FGJQEFN4>I{qg#EGdLJ;hIfEt@eX)5n2LA9ABN-chw&b82;Kwl1P9=q@D{Kw-U4q38{-Y}a<CL$4*$go(Tt5>D8@gc7(WZo<A$5@v-mE!7~h4jg5&X3_$1g9pM(#Gt?}0M`{5MhkHWF|qxi2V#-D(L@F(zW*dNcvAA`N|$MDIpFFqNc4ioX|_-r^DpN%hoDfj~XNw^e$68{Z+8vhNx74F8j;%~xZ_?!4~cnd#{Uxoj|ui~FWGaf$Yv+@6g^>I^-7bk0m7su~|9q^=tsAAE@|EK?r%YXkf_b^V_|I|hQW%w%#-oG4F*p_{PAt|Axxi>AGa2InA!YQ+I?fe&-0mx_'

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
