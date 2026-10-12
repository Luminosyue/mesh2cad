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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8c12a34914f41c18bc4d2c3a9710562/part_002.stl', 'relative_path': 'b8c12a34914f41c18bc4d2c3a9710562/part_002.stl', 'source_sha256': '6df18859c490f069b4d3ce80df752dc67efa555e63d1ac03fc42ddb307e94ade', 'input_faces': 370, 'input_vertices': 353, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.04964253678917885, -0.034636400640010834, -0.14984330534934998], [0.050331030040979385, 0.11769641935825348, 0.03998309373855591]]}
GEOMETRY_BASE85 = 'c$}r136vGZ6^8qP2#la?!r(f?HlVB`n<zXO!3BX~Qv|_57z9PdVO2x&q5?rwKqF#Q90Y^l3Wx~9@>m3n1|)HZ=x7oQXd-cqnu)3E`fmC9_RBdr$vfws|9^kouD*TiR#kVunWBDGk82RPPku0P%iVV^$qxc+wSor0^peu46UUZJX?x@3TM|K?P`4k!`v(l`Uvy<6m>%3#Fs@|E*wTXY@(Ru$-?gB1UcvaAN~e~Nx$)|oO2?I0z3-SwQ%a0JWx|-rCFXm}j-5KT&g<B!b>6JJ|M8P!Lde^8-KuQ{Q#S<bd)k;zzH*2Co_xmX=|knqEC#D*uIQPerzWjk9OA^y<(dA;{!R}*czQ#op1Nj@(=VG5=_jbMc36mG=WfaL4{AN{^mk`$%+xC;<~|(8+40kDkvJEex-8VI6{aKlv#Y}M1;-Xd^x$BZC#{}Zd@!O{blUS&=zn|5?Gb(Gu;;9vo-{3@r_wjC3H=*vkLt6?=g|>6+;tZ`k?p!fPkwpajL`qNx|<^YE4R%H^^?lCX6nU<(dRrB@lW>q=l!AnM(^@SKl5DPQmYO{^s>juTWb2|Og;4~dD~ZeOT_;ud0W0RqNi)_c6qy{S0v8#%`R`Lz3)Wy)L!zov~*j<|Lv~pLjP{Zrz7#-?edxYa8TOy`%zi8JczFIAiB<j=sFLg>pXaWl?Tyv9=xvd;QLp3@ct?fK7N&lWPXo_vgJW^od?l%9z@r95MAfN`>Q;NuJhn^l?UIy%7gb;dGPV;dN>LF0oI3pZha6vRim-fzhT_bldqo=UT-qDFw#%5uFFGe^0dtneH3{Zwjk=i6#Xc5BD&;f(ZOh(&ANtquzzL5KW{R5yVI>dUSH$%)WylIk^U=(hWQM(PmTCjbSBSj-i!DbZ+Cf4t=k^)4?ZIQD@!AJ3u<%=^PfCcdq*UnEu9`LtmdvOy<uUft9?ZD;xBSu3j3*F7SU7f7H$mVIkGG2zqetz)zkGpj`|PC-x}(5+U^YX(fI3i06n%2pvUS5J?{$_Pq3~$q8E2{@dWq0AJJ2TiRY3wk$93LoF2?>?(+QY`cO~b`h6Hr>cEg~nR-x(UbnD3qU(A_kJU4Jte!>J^(?xsXVG;%i>~Wg;?(tw9;;{3bv;Y}x}MQv^^6{?XNgDGv*@~>C7-&UMIYemB;9&M#6NjGb$-X-h<`=V31OY5kCjFIi*H6>xFqWTrmMH~BReDhWuH@rUzA7u^RA!{e>fbCe}>bOkGc9R>s4n?*#8ag{w?+HMLRO}^zawl{n*mJ5j}O3`?RB*$}{y~^p^0xCH3{}Etz_<Y1Qz)CABMWYee6_$<4?6$|HKv<2zU9RR(Q~#B->jtLFosMD;C=T|Eyhj9%C7)$TsB=DiWUxM8=j4wI7)M)Y(E_jPZ(I`r`zaCMbjFeRd=ySREtUv*+MKWcsR=T+;Q*VQ`a`_b#zv08Jo)(?8De$Zp}fUfJIB9-I%QR|rKdL0v8uVX>=Yo=wZE75gbiLUEPbX`}X>$>u~sw>}*sw*Flsw=Ony7Jeh>PmE7SH2%rS3Vw9S3dqarQy1i{wf{Ob-nq#se1GAsCx6dsyE+{s<*sDBd2AnH_>&yiLUESbX{+$qT$oB)tl(Lu8P<1>C`hzU5T#iN_1UUqU*X6UDuV@RbBb>sygv;syY!}*NN{()rpT&)rpTs)rs#%)rrr8suLfNsuQoPI`RFeI!P{R(z$1rIuTvhiRijcMAvmvT-nF<qv}L-T_<JVoH8?8oroUW*U)488hUJBlYaERBj?ro4ti|gk$&{PBj?ro4!Rz9-;dsp<ht~JB=P8dNBq_J26gjiX3M|mv3a_$#msE=AiAyx(RDqDuInM#G-+<O@fAI`zo5tV7xdWvf*#vnMA!R^oLBD`5~toT&|~|B^rQC+iBs<v;;;7wxn8|5$a(d?AiCZcq#s=m*OkuAHol_k@fBT<ujqPwlP^zo{pj}<=&|<|=&|<|=&|<|=&|<|;;-LVpvT@<h_2sPNdNkMh4}0D6%xOGZzFk7^Umi%&AU`($)arYLUcVZMA!2|bUiOb*Ym>bYF_yBs(In#RP#b~JuiGeYF_v_)x7ZjYF_y3RrA81SIrCWuiig+e>Gpczuq5ToZ#Y7&-J3~=X$TJ=X%lgbG_*Lx!&vQx!&vQx!&vQx!&vQx!%XAp6f-|&-Gqc&-K24^;|Eyey$f?KiB(s)N{Sp)pNbir+TjUx_YknajNHfAE&<mkvR4JkNB(SdeQZBz0aGzUy?ZW{<vVGJFkBKj~;vfj~;vfj~;vfj~;vfFaG-dKYHx_zv%k?zx1!)|BJtV|1a^Y^;2~HzRu@I-_J;X)Vi7+bnKyQ`4m02AEC$gBlOsQgdW?E#9!}6=&}7sbiE%*|9U?Xf4v_`{CYon4PCEG=&^MPJ+>~1uGb~e^|~awUYA7I>ypH&*Cq7Wx+J<@m!yBaE}_TPCG^<3B=P8VNp!s~Nj}xOR57o+s~h$Epy>MdLD6;HdVf{7zJFD>qU*X9UDvJmS9L48u3N9Gy7m35y7m65Zhic!Zu7>ap2(Ir(RJRuzxrKObe&J%kIJX-N99v=olntqKE1!nr|3GLURU|_{i}R>f0a)kzs~2&J6DDN>UV$9_3!?o>)-vozxv%@bp5-(*Y!A}>)-vou70ogy86A|$D@9)&#T<!^vwIlqR3x$l%3l4m3Qg}fwh`JgJAraj6dnHqWuVF|C5f1=l*wp($S^;|NAE$HtaL)b=gZaR-f+{&&X)Acs6(zylEl`nixxhJ>g0C0I)y&kLH+<jGdZrcuK<YQ!O{v0&EU%0q+2|hqp4vv^3Ti>;vx$9|{hEk2ZF-vBBUF_$b;2frH^ThT6s&gSFr_>~IHmP#rdepI|H(zg&DRH^UknXYg_`0l$b?hk--kXC>UVT?F=pk2H3?Id(W$6>f9egZ%b~Uj|+Px7ZJE$0(oUdcu2vdGI`rvAn*qdbHQ0&GKH1@j!3@yjjB4L@zK2w{1o6Uhv-FAb4+hA!BzT<1_?57%YSr;y;)^dvpF~@aAA4yg9rDHB-QO`oJ#)Tfkf3AL`WNIba9)X@RTV0<Z=AOy<s6nB}d&)8Q6d!tGqEM|(Zm&Ip$hH}_hDXTuv(fB9e@+_trW=fj(TZQ)JeO_@{8m{;xL?ZBq+rues`&nBF|A-oaT6y6A)%Uo{Ed78tUfw}Np{F^bqs&h>i8^Cj!V~xO^jC17>OAd3<@@mGa1a7WWVZK;y=aHQ^Bfu-*tr&|-z>DDxO<N;l?+4B-{{YN|TeG|(aBJF!fm_$CS>70|fLGw(n127jc`TlsaQsh!TPsgXIJ9e|<v%w(Wo!W0AO0(24;fnnJ`Z05-wvkX+u?`7Kf@2h&rCQxBjNZV!w=f=NI0{+KKLHoVm;Q3(}?Rtus{6tjDCM+u%EHZ0=GV0m2hj+S>)c1NgZP+F?Q#hw(iC*0WXGI90_klp6oi>pZ;vW4X7tO&+Piugg9j$UrM{(lIvmh(QIs&($70K9)l;s-{t#H4VD-iA2>dX?>mjXZEOc-`CDM^gyR-#!Rr{TOW!XW+r>F7%K0o>AIldTd&bxUnB`A{JK;My_tW%a`+e5f5@Qb<dk%aS{wzMv(dTWPXEFRI#>RnT!Q0?<$W2|$a+{ypV6DWD`Lq05bIb&CHG%w<WaM%zI1c_GanAxJ*R$Z)f)n7qjU|os!YuEJS$+Z718(tr_yzFp;Cb-w@NQsNcsF<#urs_1ypyqx;JILDcsrAeHpbe6ZQ<6=Nx1fQ@DAX)@DA{fU}tzocqh#AE?`%<#q;16yTJ#Vn2LzEh!`#Zhp}&sot<#lI^p;~4X-rz9X{XT_bvQ;uo7<1m1FFLjPvHu&%f}ig#Q5Ao2MW6Zh0c%unIf@uL>RquL`dQ9uKbuuMXCLSBKXGbKnwhO~%KLQ)}>SxUI2kjE$k*dh=bh;^4>J4gv?m2f>GcL*YZ<!@$eo!{Aqd!{JxJuLMWHuY`{TuY!++j{---N5QWKi{Zswi{*uZ`&@|GPan*F`eOETk+Cm~eQEnhIQ$B3@oTs>%fG?b9`k$fckoY*ePZlY@Hg=N#`YQ82)+bAX6!TCKch|f-}r9vxA4Dn%<CM#3I9!K`@v&yd+c91-r{TUSB&j7wjO)|e$?0z+K<p?`Cp8EY;2FQwZ_&N+YRo4@4;s`$L*otJ@~yqu0AJU77xImG`7;%B4g8y%`mnQTm)Z)kL7n7yTjP^;C1jvjXgs9BeaR{?f6-o2)8~D)BZ4Rme1z6N#OPHrJQ3ncqjaEW6O-qH+HkJQe$_4^WpRHvHV_R_ZXW7PK7^VYz6HrXtR7d=eQf355EVT3QmEq;Fx<r@ttSv7se)oH^Iw{J!WjKu^WutXlxER7d{ss%kN`6W`Z-|s~F4sz(w$18oS@vt>7*2r;M$peKl>CziI3ZW81*3a69+Dru}Q$EVngeYiSF(8NLPnB)Af8YjGW8Xz`H@zLxJ6ABL~zn5E#Oa66amoZ0}s2;TsI99#ys^K>KQypeITd>?(i1a5%81YZt54&O-I3UE2R+}N+V&Xw?m-~xD2zeJS=RsYk!`uzAw*?lbXk3agz=<B4+Bi}N8`Ik#Y{i@mfWb?pNC7c{b?2aA$8?!lNlK'

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
