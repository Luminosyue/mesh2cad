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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_007.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_007.stl', 'source_sha256': '4e79f4a08bec2e26d675c8ad26cbe5168d8534c9de30a518a685510db5ab44d5', 'input_faces': 472, 'input_vertices': 288, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4483375549316406, -0.4719848334789276, -0.48443448543548584], [0.448323130607605, -0.25560203194618225, 0.4433556795120239]]}
GEOMETRY_BASE85 = 'c$}r14V+F@9>?z(WDsH~#^g!64P{j*LlaMH^U^ekUX+z*FtbExkebv!OC(|2B-^5%yi~SLO(<_Q&oVNG2{VlMj1Z!%(hFAh{_pvoJNKSvc0c>sozLh0`F)??^S|eud+t5=Ip<t@r^i=KwA9}<)}wuAriGI%OQN=wXg!{lGj`bEtTC-ej(#%Es^|Ffr*&4(`!aez7-v0hJ(V&fYs}!Bl#YRvwCvQBR)Li4Q8{CCGDi*^l`|wu{H~cJ#$?(4n4y`Yv+U0;+N7qo3bbw6D)4mRfBdT{ZFn(nf4=CYcAtv|#|<v-?DbDyvsW~LAD)@v_#yJ6J)T*X@9_ipf!+(2dGmw1oV$#C{Ae$gUp{HU9_M>qPEN1le6LS_5I;I`fa6Dhru~PW+}+vhf1~m(?T>kJr{nAM-8G;r-{VIpKa3w(*<!0V-}-vjKA%s$*0JyQboTnXon}7miGHc_!;3l<IsK{oq1%jg`5xcxx5pBfdVROwCJb5XEk|Fk$X#!&bFSmU9h;oI!v5Qw@4MvY<$L@Hez4nuJg0vatlOmO4fyKSegI$BYgsc2o%}Vkoc;=L?Y2$)U?9`+tq~`7ROSaeEcE%|!}mLWbWQH=%KUK6PCnln-&p03YhS4!x%0HY-f4{-KQueMyD~pAaK0};nlgW*lh1is&o(Ib`uco>f39BQwDX$rjvwHBqhneYdwtyx!N`T}USIcvnXi4FZ}lJP_~rDEwd+^KUf=DvWk31yb-$VUZhz|h6&*Hu`!hJ>?&8Y)aK972eBI9hBVYR=@*|y6H+uU&65q4f>j&|J^N;)Tqx!lS`TBYVbbh}tKXv?5&D4FnBx9S`kDmKsPi214N+@;O#dX(y`P^uU*AEZtUupT;H_O+)S-$qo@}tk+sLG-I$ksE(USHQ6eq_ORUq1E5<l~$9A=(pp>6kBHw=??UJYT*wPqov`*X`H&;rSnJ@U}lxCG|6}uiGE29rowb&X|0BGhesg>eb4ZuiGDPlk3aZ?Kksv`*nW#k$M}v<2_n5xybA5@g7-qcd6r_JzwA*@8#RxDf0Syyhk7F=*!pR+RP8&N5~H)eP7@m@1Z%%i@d%&-s{}z%a1Uw&3t#flOM<`Q{^+R%a?ss<n{G<4_QgRd_AtCMt&GSNPhI29R=R;9=!fkk=NJbJ#c3eU%npimXWW=yG6cLmR8`s->jyWHhX>dek+(;;>+j0ipkgao00F{ZwJr%^4<IGtJ%JM_kJ_--TRIFNaLT@d)ptVF@B5JciaEjK!3h|&Y1bS{YJiSfArqrzI?a+XCL(C>-L-ZZu`j(_MP>2-*{i&V{>JGFs;<*yU)+%c_o$k(HnmBm#?1>X8HPj&GL2snC0V}<-7Oi(Aq^_-@QMtn^x-e-SIfNc$2R^dOXfq;>&l(qml29M<d@Ik7sK7+T;E%AM&?HKd;J%&heG6pI6bv1^)Kv@oSXtj$fmE{d@~|U+*hlKi|q%EcNBP^ExA6Ki{H8z8>!ZqyOFUZuGx99_w}5T$vx8y3yym_xav;N-FcMK4*NsJARGw-Em=*?~V(jeC_M<%O`Y-I_)&(`Jo^8=R0}EygmHFUmZW1GEVi+p4qA&CO_-=p`@1TdY$;adVcmB;`qU?xvHNx{!aN>w>f@!ht{e;ci*GRId}0Br<^$(ls{>x<A-ZsaD1!o0X0uZ{H-eI;9kcMSDmTavpu5x=~2fozvEg}&NEY#e=5)MgE@zsa)R-#RlR{ps+`wXt8!Y-SNYXLj&D8>wQoKT-F)MD=;j;GL+zW-L+zW-L+zW-L+zW-Lo2bpDkry0m9u1!I^Q=+KlYxN{@u~O`8(z28^2R-zVSPyee-up`{wVI_RZfZ?VG<-R@?^Fo|$*5b#vWZb-i{hQhwLA${(Ad{F#}KAHHRmYR~zzsy{EZROR<<;pCS$nW%op(@NGl*KcEyYG-yERnDk|jvq6Bz>k?f;K$4#@MGo=lOm39&VRIT&VRIT&VRIT&VPdO*{YoMhU$Df)K}xH(O^}tF|X6UIj_^cIj_^cIj;-$en|DFF)!7=IWN_|IWKj~G3KSg(XG{WG3LqIH|NRG_siBee)AemKZM@wrOIi)&hf)LkE-z)S+3U6RVO%pdBe5pdR;10_wDej*Ld%%Na=ay*Z+LAcYNt}g!avKhnsJ#JKTI@-JyMR-JyMR-JyMR-JyMR-4RXSsr+&8s_Sxdvbx`1z1Q&r&lalw|N3n;j;=ei%6q=<x(`2Qov8E8b)wEU*NONs>qPvRbs~PuIuYMoCr10uQ~skX)p_apSneyn_Um=D_RaOR_RaOR_RaNm@YutSA3m_x$q!7)VBhA@O7A$0_L-pk7B4w|WOkvtzS9<|{+~K&Wo7NuzS&Ogo9)zo%s#-NM8~)C<DK?c50t8U*B<=H$uss(v~TX8Xy4pF(Z0EVVr|>6^3DAp!*}<8@MHFW3}5g6SaU`@e$4(Ae$4(Ae$4)r;p_Zh&4G?@?!Rf@+<())x&LPRIzP1YCe?oSfy3vlgZUmm!ai{L9|QOM^7VeQna@6Oko@Sy`s(_c`;GYKeq%H>@S*p9aQ7|o&HYU4?&J@B*U|7}_DiR{zQT814By<34WFB_!rRZLZ|?V69dBLXJukQX>BrvdTuDD`-|S~M-{@yI-{|MiiPI~c`i=Q^^yD8`Io})e^JsG6r~k<hy8f3RczwM;AIhlXyw}iv%sl_5Y0mu1e81rO#`^`=H{LI}zWILP=B7KG{?X->EZO1p-S;D|f1RTd{eEQg9qRd~eO)hpDD7mKb6&>#BiA?HAC-5nyVvO-<2{k<o9~0tH#vUH`ylNb?}Ng9^VD@V-%sKD-b3~Fy}dhCKVy2Nk$sAGBv^@7cBbdmotW~cwenYY!`l5<ukPBlZ}b1Yy6b7Tp`RTS(J(v_&PP|m`S4lv8(7qeQ+yVVk5l@cr8v%xf7pDH5I&Bsfsex<pijUbz>gEc521bFhv1vg7Vu4QGc*Zq2H%LLz&FAVqW8cL!sF2Ku;^-d9Gr)qhV$TKsPx4#^dkPZc2u!HUqa7ViY0_k62dFcweSk~DfCJBDfm9LFMJ<-1KJY40ZvAn!lKv1$#5(5Ubq!}Kbi~Q4^Kcph9|%uqTj+F!l%$n@NewsYDcymo9)<S$7|?3_%(P8Itm^G4@I-#Y|0eQvg3DlbitGQQqlHsDtsr}1@6MJ!gKAIZ^uYHDK`fl36CTvhxW_)>_hj%``|)yrQ9O45H2J~_%=Ikw_|`EZ`!fQj>phP;m6>C=m2;C#|o#}(aDascv5aVv@P709N|(scG|HRPmT|v55pmNEIJw<3%`Xfh8I)jTeM%!rv%*rm%v|;EA2RpegS_$&SCnqkmCyJM_tZb>Y2;6SwxJapB{w=pjq$$_%^f)d>h;rZ4bAF)6n0*Y4F2nHY_>{ei$B2jG~`J=fR8NQgjns3V(s_gZFX%!mr!$h8<JU>F`u|7&;st26sbyz}?^uXh*mM+#S6O?hZeKj({J5pGRlF&%+UP0UUvg(XDVXd;t9%J^*jweC7N<L$|<N$PwOU#~wSDpzpv-;A!Ygcp5wi9Rd%6gXpi}AbbmYD|`#w8NCDU3}>Q);Y|2B^ac1i_-*vB@Y`@1x*INok8r+n{zuUx@DXy361(ZI&*9IA-SqKp>Ue_?o{qi%zd*aE6T-vMJK*7P5A;^J2iy_;HQW)tix3`x4uMC&GtimvOs?w;LU;kX2VMYgMUTQq=?h^Q7cvI)*b$zJc85hDu`0%$@au%|7W8>oGy-pd51_^HS6s8@=n{B2JO!Nwiw=UPz`rGg+n_<X4IDskfkivR0r+M@xIdZ+_lGB=&%vT^!;|4<gzyQp3_bz>%(?%}dGCUcpk=VkSAVe7+*b7OR>fRbcq00&RWUaf?uqt>d&0j!uY-R9H%6Pljp1w2U&7bI8E7v!1O5X#3H}582^xhzfxkn)hrfemPW}VuUzNGLcvYFZe~&NoF`0j@x73_p^czC>pXe!A=6lcBaW^5{j}Q(M&rse<cs(Jk=Yhf#(EH(5aC19aqq_X&)Y+UIVVTojWy#V^h48Nk;j4+OD6ci#oVd!WnBNK~qc_0!!RdB9fa>zosWY7%VVSExZO1x7_#;C2_r%kb_W+zuJZ)9X;f0?<SHM!v*OV=K0Tw;!srMwuh*pcMSZfHM;(7}Ilj|z1uX{Dtb`rv0Q<v}s^dxo4`cCHYYtWD3HSiN?F8l=C2fY{W1Ghl0hg-l&Xj3=|PC;A3DeygLU-%w)Jo+R&9$t;Eg;&F;(KGOASk`vma{g6V`-)eEweT5ynd8d*Rj+e}kHfOoeTxv*b7tWX`Via+)ob1m-w8M4`%Z8>Lil#{Myp~CAgb5AxAUFwIKCeU>otY&n`oX@F;5pgM!d;)$2rG~=wbLU$LRfm9ULcXDp^ORqB&N@T1>brAv_eF4~rJTLt(uh6n+ie4~uSwWlKl4X&Ms3S6Z^EV_6OCsBcF#^a?v_*>M>xS{1HJ-W6yZ$HY-qeU7bX#~<ye!)M`heAX;l%RcZ*JL<<Nt`VoctA$qszo8wC?WjY3Z96WvBgu|taDp8*?Re2r`E~g$?W$`jU-UdInn1p21M(YCUrp*vqTVFxsY9K~d`_lKm(yNpcXhO$hp*(bXe0PXOa58BI_Gn69keD~2d+i`%k`*&R`+l%KGz~&INnl!)d-7gC4V(6_p#@20(~NV^b>lyhZFdmK)&#0_Q6-s_X%(VG!bq9H>3}xPn)1u!HIA~v@v|O9Zl))W^gjv2u_BjUu$u1%KdjG_fBofs>3~z!1ZrH-^J6fRblC;>Rg)|T+<)9K22y-5^*){`iZ_cPaj@Je;l%TqaAzE_hHd(9$v_2(LckY1s<Mb$9wR5d?(&t_<Ycgayz!$@u?k4?bran%IA0Om}SSy_%HLF@G3s9BJX8%HpfUEf5VewUZK4kspoxS19dGW?|pP3yq$LLMZbg#sCyf+igvw6odv|ZeD^ACe1#Bx37rMM1pmp7-sy2w6662fe@&_Q3p)eE`yW-zBmLXr-XlM;%W^l#d#6{EF=*dpRh%D|S7mi!{R<PXgK7'

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
