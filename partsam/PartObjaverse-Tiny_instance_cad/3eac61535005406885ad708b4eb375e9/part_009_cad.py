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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_009.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_009.stl', 'source_sha256': 'bf36b834bd18adc9db3e7699fb71574070ba6837af884168b43841aaa975cc50', 'input_faces': 360, 'input_vertices': 250, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20364820957183838, -0.4304780066013336, -0.22451281547546387], [0.20363497734069824, 0.08154299855232239, 0.22451278567314148]]}
GEOMETRY_BASE85 = 'c$}r03s_C*8poGAGiJ)j$Yt23D1>s2<BUCNTt;X}Zeb^pTbc-wED;%@NJ7|&3ZWt;$;Kd;NHgvYTbjenG$!|En3=QI`~H_%%bxQ*=Q$_O_xykRx4!+ZZ++jl*WT@T4ysYpM&O@T!qM}Cf2(XP2y&}0*a&m|gXc{3^Pk-@FetQ|U`<~BQF8r|5raKPR}<z63mqo;&-M#;=%sV$J=xX4N#`(mR`8r)-@pm8f+zXQzMt=m+5VEB9pD?}FFkhb+|AiZ*QKqKZjtVP{CP(nL+b|Tk4s^E8hu+%)7AWo$5md0H&4vZS9=4zAmmmQsJveBe);)*R9>g5ul7Q&-%ZME+Vh%n*z5eX=QY9$LcZp_BD`s$_PhqgE9dQHeS-R57<+;0M8u?#Z}x+U#@~4YdA;AU1LOx^VZS7hys1n74dh>CkQWw@Bd=RnoJ9V{6!PNZM|>S+2ChG12>ViZ_Msl^AAQcg-hJ}sutEFCM|NlbsFt>W%Pu^gPkZqE+4SK40aols)Z_VxjpOmhKRHf*r!Dv2=N?DC@D}^jYJ6R*g5$}r*-ze-REO&XPUGux+{^usKj-x{+ZoB9Ol7}rB(MLGfm|nQA$j5DK<+=!iu+H#Nb4!idrapw*8h;NtD}+Ex$gs>|KTt9l3#HBD2>Nli}r`<fi7O{#q9aiU)+8-mArKp_pkbuuWQczt>oSIk{6V9w9VuCF=cslzUiy@yt_~E`nEYn-qd{w?~^TaxsFeRyuW?Dz+3Edc#C}wZ?Vsn`fu-Zc#C}wZ?VsN7apPht}aDX=k;oypK064>uNf%ukXe4;Q381J$}@e{betn2ainh#v?t+>whsPlCM9E``<fPO!Wf$r;rbJCvX1!DX-U8-T1u5X5{sg;xCbpc$}i~=YHV+n_unWaSH5TU84H>{n)n&4|C{x!@lA=slGh^Nk!xZtEZP~JT3m@`tfIS)Z-Mx9k!9LN+mCzd`A66yW?EH&0_Yq9+DS&EZeH~I*%QE-tr0D-^-ipXU4JbsOSF6hjRaewQ1f=D>Au%?f~v@XU(sRwYj^v|0jH1QCDc3rhw{vT`k&?H-*3EeUtW2p8tQfBySx1n8%;ohx>>Bc9{CFY{>VG6oKy#^KXzBH-5qUc}!v~`?KWr(e`|QD7&(jygr@1^APH9?(W3%d1E8{*M0f*(jD^?xRlR(4fkVRD9`h@>D(XZ)wkBAlfURj-moB)=FKp771uvw#p7Hzlf1s@8SjTNH?wJceLmv(IUI%g&mnKNx8?QCSi<uYl|f#Au_gC!bd>9RrLdnE$@QxrSWo_;$o}#7)L*d8Tc`FyR#W!tb9g-BqHOi}^&V^ay#4f=I%ba^yuNd4lQ->rz;)UsbDfFdhj?E;WM5^^^En{vAoZU&jNiu^HRn1uY3x0h^ZU+`ne2n7kk{9Y;``y=rF%8Ly%+B{W&UfrkQY1n^SZm&SVO+J4fh|uk?V|a8ACp(8hJr<aVKBc>p1x*&$GyzmQU}a_LC~fi#V^o^=qD=KPtF??n>T=eFw1*{*k@s^O<ygbKB>Ue|Cqx5Z9RYyW)R~U~gMCm*)9e#v$@4v)LQ=4cGX9_t?9>GhcpeUVPd_{`{*<u3ynver(D+#@^=?`;5#fbY01ze80Vu!``vOLiw@Y?mqYLoPjzac68q2kR0;k)7gu$)2Pm{-dratP19d&eoyOzs?DJB4E&DkWbI^M<+X_Fe13rY8#b_y;rgbPEl!Y+Yr)=F>c{gE%5@5AU_3j#XkQ)m&m{lB>kN&5@+wE;V_Hp>9~(QDbAQj`1LU8@F4wGkS|<D4!?d3aiZ4!Mzq`XR+7ExU+sylL2m93K<c0Lwd|%2RwV&%0t)x0<|K#xm4Agkz!l675uCMozKfa0IC(XAvtGzfPlKq+-uHXDD_ctfeV}1YcxK5#weHnX0`4wJYT?G5|#7H`?T_TU?Vz9=)S(o|U*k8(~`-o22Cys5{2ZZwcDEq<Div8Dp=ze5S>Nr)Ulb^x;->k3Gy>!hy|N15OcRt8IAAVIG?q6A#ef0DwsuNev<9YbgUf$1+tEvB(_p^Balxn>2ZGXOAuWa_k`C(M2bS1B^A(Fj|OB&7d=%)qbs~+tkf1?_mSC_k<_fOhgtxqc8`p%o#+pLJtjMJwd`?Alr(0VER%BK^1w^7?QKB#IpuWz3(DA#?=pFf>0u+P3g;}rIF<M*kq2UF?s=+Q}<^>R&Qzqu#ZSJo>!j{U^wt(yH)8qI#hHmajn*3mUk)BnxBQatLvS>J^HDVpn5);B?9U(Wu``W80a$?IYlL$9x*=RE&&eoiL;{U7u>O#Jm0`-?g3FL8g}(E{wxP3-H`qW4Q<avAsUx`O?Q^*iaYhduUT)eiDgJJS1^acCjeDUW7<JBmKvn?vex|7A_t-;YbC>l)FTeMJ-Y9@7#je@`#ac=O#^a+(}=vyXd+{jRTRoH}Lx-OH2IUa!n^#jzw!{o$Ln9`y|Y3G8>;v-eNhrJ4V<7e=*zGymy@?5!5kJeUV1aQ}>@?89t$UBdP$`<cDV5}u#mop3+z#J)`}>TkYg!0WX8HhNtZEz987JJvDAfxJ-nZW#4n6pwvn%f9?zg64V?wr=IuOHcCRzQJ0rj}E6iHHf`_4g2F(^!uc!><7=9<i%ZMXgsFqO73s)p!pToCerI%RQ5w*$QJV3inzbBABvlh7sg%Y-&do$vDc5=ME$RLQ-5Q;%Q5zy$O~PE()t^GniXh#Rm5ysFU5P#OHlVWjT~Xpc=R_ae$>w!>AYnpY5XQ-9Ze78$v-{K<5$)z;AT9(UQ9H8-Q#lhwtDv0B4{1-!W@&vo0|2b^q#>!s1^HO=`^o~&)RCeZnd|Z#*CI2zhOO%M=&4K%)colmVDirhcxq9>`wbh^l|3?r?Ic}i`P<pqXXa1r&Zzp8BAVmUrPN&W&Vo~t)c$c`|^GMfiK?Qr+r0_yG-TtD)Zp%x{~@wHRk=;{{xf8i>=(~@jw3HIx)UcJf2x2>AcGRtaM{<|A^`sD#o)fUJ^<Es+sQx(Iv+;-m65U>skfx{B)_hziE@JN#oJqsCcv0Z1S!hf~bG*2Ru$=Nig~N0kn_wS#>d=m4W1A8ciqP(T%+r!hTH&^*1?<W-pBLAz$%w6=m!Tt}hI5*LdaiD80kT-v?NH{{V0C{R6zk_Yd$E-#;kz-~Rpq-s1ZQc#H2J#GPO8esmv8IVp|jU)Vg1@?jwDbN#z_;G2wB_tz`?UwnUpy1&`h9qZC9h%%=qy^okq`ry8?buQ(zEi`YYd*`{nAum+z^~-wUezkx;#|ull)BBn!+>h%Bzw!4>bE?zl5dE1Uc%QA@$eBvdGq>rAb@5K1T;xr!3qwdTucP&aO_UkQ^f}pF+neh+hHT;Iea8FZ;}ZU!&Gt0=KP$OT?sfj$QuQOh?+QB_(mW{F`)v*W{jVyTuG?7OpMAJB{hnm8Pv9-~3B1KVfw$NvO8vL@3B1KVfw$Nvhpo^5?Kt5rzJG?d`2HE*;`?WKi|d8AxL$aR>s7}2_Vp^`eEWKpajLJ^Q}fpX+ma=>4Gp9&QmZG}2$OwPe=3lr{G;UG|EXYV*Z=BI1zo!T-+wANERA8m)Q(9_zU~83JB7>vr=rhcIQdvQS}I(s>Ua+L6!HZ46u1DXoU;IY0J$H00Gy6Y1!qbvS!(-`3E&K=ZIYKBxeFYJKFM(Mv3RsNxH#4EUEo|~CO8+IfmF_!0p5g60B-`vBjdnZrM5<D+mNfkJERsPwIpOTI0}8%z{$r}phdw&sg6g3laO1%N#Gqw<(xafG00Wm81M>Y6nM4N7D{a`G8DW{YGG1~MJ@mbqR&D&`PfXfK)68F@de;m<Z5s%cpXwX=Q?m0G87yJo{0<uhe&OT)aD{5g2Sa2AhkuvN#IfFGX+jQHWF<V+$h!YN#I4u5bz>!I8r%hI5+?~5gY&>i5vy~QfiZ>7L4=-&zG9N)aD`mz&_|R8BRVn7R?9FM|Io}JP-LLcpi8@QaR^*us_ll><=D`^Z|=fn<2F&$f@8+sZE#KGUPPyc=VY8Cm$P!HXd%g>i9J9GNcGz29883=ZpkTM@|J#2aiLJ2Ny}LSZZG*FM{Pf4VLq$iu3VU&OP9rQcICq8gef<4V;I}2j_v$AWwtOfG;60f-ixuAdA6Qz?YFl;LG5%$gja?!AFos!AHQmk$b?q!8?&D;0;J4G7W45XCw2#+29MvGvEv0+sI4c+u*y%E8x4}QsiZDDfm3{EciV55b_B45O_OsH+VaE15&xxe5~IdWD0majwd3G;6(62WH$I9_#E;A_#F5q@;3M;_zv<e_zw6MvJ`v^T!=gmE(B*G4}r75TaeqqTfpm)8^C2!qt8lcGDo1Tl-g3{SK#mQoPQzjtJs9c_rWKT5#R{akl8G?@1$0ayaz4^KSVwNZ<N|%scl9sSMdZqmeT-kEwwgMyNbL9z6!2Dllf<<JwjebUISkTJ0RPD>mlnR+koqW>mXZ$>ws%ZtrpTA*&1vQ{uX%^{4Mw=WCi#q@N+boUm$-5zW~2fUFS<QnX9DsEAkiQBk(Wa8_4V68(>GI16Y|CnFU<u#~52B#w+I!s`3AT>yxuYb-g8+j}p|dN7e#YqV8kl3-Dv`6XZ+q6Yx`H75FLmnQAVcp~?Is@)z)r;BSyOz~6xFkd9zGa7|=Aa7}OxT$B7$8(9rp8(arjUHEG+$y^s%16%_&Wu7Co*-{Ha&I0$9+J{neL%s)g1NTAJ2loN%kv3pGxG(ZUa9`9KjT{5E!Sg>vz6X};jKF#1^ajh%?TY8i=?RvPx!|}9j=8~m!^t@a{JGTnORWd88@LD971<r^3LcCc0Pcxe?U6me?ZHk+SFjVfH*zqzx2oP?)RI|;Y>sRXZVqmNbON^kw?g&?w*u>sN^M(YBV==MBXDD63vgp_6J#rJ6R<5(sr`x68cNL_`7YQU{3-Gs@TcHj$OhnE;7^bZ!JnX(7jihb0iNFw`7T(l^99Z$=P<DR+<)Ntat;N{$2#D62OM*U9|kAq5b$SG8z{9-$S&Yc;LgZ@f;)rzAw9qyQL8Po6Syt79kMgH9oQM!5A3X}*AKO1{s`F=*%sUs+zi<c+zi|j=?rcO{s^hmwnDy-YzlrKY>jLNwg!J7HP1oSs@v4~PydzkuOCsq`Dy-R=iATJeyyW^W=CmrzWI{Jb5Je1$5xmA$-g9>ldoL(H<~VllK'

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
