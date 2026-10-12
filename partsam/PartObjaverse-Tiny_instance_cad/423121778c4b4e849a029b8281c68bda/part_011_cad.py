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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_011.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_011.stl', 'source_sha256': 'b51149e920048634215abea3b86a721b2e82b42484691b623df2301fe6283d9a', 'input_faces': 295, 'input_vertices': 208, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-11.430607795715332, -5.441899588731758e-07, 0.9046998620033264], [20.19225311279297, 149.9131622314453, 16.866796493530273]]}
GEOMETRY_BASE85 = 'c$}r02XqzH7KSGfLMISH7Z^fF2!xgpdKu{gkpO`QsNp6MLJ0wq(2GNrCZU8L;nJ1fd%02-1jWUB(!C4OM-fC>C?d!^XaE1@UGL(p_11fFZTG*wvuB?(XXehFGmE$mx&4C;{8ch?FS<3`(4n$I>VG4W(=!M3NzSO5HgvR~QB=76(Jy$rTWnlUKVyV3HoR|gMxXTXMrL@EehtDS&G3Fh(lgT&(|Qj{@0+Z7o5a+NWW_W3Ck{<kan-2W4I<6xh)8q1`9J;@P(yHzx*q0I-pm`3XesYnJ||RrM^u7vYu_B<?$`;!oiA@z(cJy)vO~w_g9DYNJ!iadJEXeg+k;9}k^I8Lg*)z~pibvMP-jwraC2a!a4T0i<RAA#ou87Czww&no6}!}N`CND>DRi`7x_1L2)CX+M1I<S;qDXQj*}a~E4?q=xG+n&vGzBq<4Q>rZoeFd`lr@OzO!p<;b!x0sI&15@-wr*pXCNm`V`|iYNO7ieU&wLy&Q@BL+gY)P7elOd0Xl`+Qx>-aqZd)w=XZ1eEX|^NWRsim2hL`b>!zMD*28g--gKf#^qrC>wk^<vksdwo@XIRa=rsEhD)8?(}g>Se}X#Zh^jIV8KZ?8i@M=_7w-kXG)lP343aud|9(=(-ZDVAxnT;<YflmIXMKfRS&uOfGa{spwL3|;y&B`RRyUS>_o25?KVh11_tVRmhr=x}e#aur!xhwbjf%neyW_ez!tzOd^F$5Q{~{00H)sLQH@GnBMBPIj{{oWlc+)_g*aYyn<`{p_rHV2S?{=5^=Gg|4Z-*z96CM~W^&KZdF+Yd?EGy$bQvmamI{>`AQ@A;#7V@h<1#i(!xZN^Q`gKhF3H|;YCfxnzWZ}j)2XMZ7E|ih^JdAmEq;5j~SEou!{h&bfTX_@4xpfD4pS<YzQ5*F8^>X2^<vVa*)3!tiPgyA3Sd073nlJ(RExQW0>h#3@aQ2Dh+kxaWe!(~=P6D41g8Cg-ppK(A#^bnMLgqPsJ+7CXiTul>g}cT?V4RP8U_5D^z;hnpzS`RX`L)Umcih5w%ms^(-(p&@%;(;zxQ<WyWBkLSg&W_^MxE{P7|-CV#f9G*g#7lOf!9b5lJm-Xf#*Y$?@`CEmvFoJui)>cgZIA|D0PyG$@tw7I4`4k4tUl1sNczn{L*=a+wB*F_nrj)TkRs!Z^kXm^O3@+^W%%clK=1;c)~>Fzn@V^bGN%C`W=)QDcpQiK;~^rC*jU>MZpsu<d-^kx1r8wIjGa@F1XP(3G-IJy70?eg}ZO!zIA<72zAyr6Ye^95aU0#h4Wkjb&74q^{r@wKii*AbH{)fsbe*|i2Aek2{+$8fa|iVGx8h9BmcV`T;Iga;2-^#S9q~#)OnbSI#*+a8?Be2-<&bXzv&K;@r2$(o!VnCpBICLJFek5Z?yge`H}bXNSzJs@xH5k1w7v!;Z`87m+{Vz;JqsdcTRr<K6e`Uk-7ddZ}VD99pmIM&coxE$8>%*ymy?D12G;~``<M;4wgp#=M`S@=3d<Pa8;-IYwFmC=lV<g0`zNp`c0^i$9l~;?Ywt{`<|B_3hw$C^I-J3fjXZD1&F_ad9$YeihMQC*6Ze3T^Gyix|p8p()6Nm+f_D6d&f5;aUIq5mDuO{+R<I|N&EM_A69Hf9d-Xm?0f&H`%UWj-f!yulzO~B-Jbh1r-^XuJnm;J*G_PC|4W|F{cmqQg*p`@g}cos)g*3u7u@G}WcRp_`uF*}^IwJf>US!2eSfEaG%P6mdUe#FdkNz|n<(5)#dFeJ+8p)Ob3pQZo&$FBY2ns|HkgNmGZ^Rn7lp<9K2M(1EF#Be;`!rvUJUnD;vwPI?MCQ#Yc7maJ;$V-&oP(hIhJ>saAyRbdsfz3@HuOQyO*PmwbI1+2iz0xd44+i{B*7J4-!6PIp%+IDdZcygnORDW<olj+kJyDUwCdi$KFN1_l}@W$$6+>DI4?ipl)&DkA`DBbvMiW7;haYj`JFd{QKV^U%fA+KcDx7YiM+^9OwIfiAff24vWM1cL!qpUyc)QRqTfOJYiry8&4H(@5lSgum+=!df&<Q;QP+$dEcq`qtxa5(c0JH)%#Sq&->I;?_W8d?_Ve1zsBT{l9KQHzRuT0xH${&ch|{jsM7)5h~{|wpRs<naBDr*55^_l57(E0f5i31i5(cHTAxVF^@-E7KDl@j<0;PdOwu-tN3DOP4%a_6*FUZYRmw`8R#-1tF-L{#^_ArLtgrNXO!9r!W7ege!mVjNgd2-S;(k!;I_bxET{l0VoYenzCh`w$z<kE_67FnpM7S&3iTgP;QMjup){W-#s_6HJOyO4kKEmw->2jY~AN-2?#kQgT^d-VwG0%jXSEmbi*9(#R$5QK6$@5vSnreM3<MCPFnrb~P=kK!~cHW2(ZXN54ekX62@w<=L5bnFKcB^%`9LIIIlk0Fpt=px(&$``K>wGy6uJeuGvCeliNkW~q*cZ6-TBtvxFZ!LweZ)U&pnlW<jPn!T4<(CZo!@;F@<XssaYqjn?#w+J^%rAb<GyfE>bMtwfI1_w4>Du%p0d=wNyg=~Z*m1aMV-z)F+ZEu<335L7=r#s3%8r&_wGDbI|S#wLAWckDfS&7UIrh&RJavgUg}tCA19vsI0yG}=Jr6@Puo43qTlSXsH66S68r22jSFqSuj2RUEPD<6$7X|tJ63VOIleRYS!#bO<KzC+Jk0%R3q$tV_TSO3wI>n3ceT%zcAtH&bv$0UYZLax#_k2L_R&(;XCLi8KTEi0-);2AzS~uE2l#33(^DqD+Sj9h?CZ@T*w;JrzrZ+4@H;@I0qFO*AH2_Z1A9^c=GEsrgB9{N{DLkx-?~F^zT-0So!}n6S2&iu#QB#Qk2<0JzOkVU&a3!J@X{H$UMVs7-L=_>_68M%oA*O-U%k8u?(_Y`j*61&<4$CL)ED?&tZItu*1NxOd;b#L4^au=KHq2TQP+igzUSEdo@3{P;dlAGD(Wx(63@wtz3_W_o=dnppsXD4G-e||)erpW6#RbcEyj5~vV^<RT4Ed{Z-YlRz&Mw-l-N<o55Kci)OYlpi8{IF<GE!Q6z-h30`s^A+}ag@{J0vZ-!Yr-+uw0rex8ka{9ze*Q?3)@ukiY2Mag&?rEPAe^MANeTiS2G6mDNW{#>uG9n%Xu)ZVqOShS3zOTwQzHe(<EsJ*++UEz*7Emj}Z{Cd2+pWOK$3b*PumUX%{^GYeHd%aX$nb%{hChL6T1?JhVUq`rmSrf^3t-TR$#r@^$VWEqk)`>4-7~1k1!A8GCuTO^>>OYTv{inkLb^p6hhYe%?-%p3L)fhfhwnmxO3zf}OHk4emO!}GBL%q0Wqm(6)Yu2BB6m^mp*DOt0FLKQi>C>otd2!A9DeFm|NS#Q2LSG_fr|C~pYdghu?T=F*Qg%Sur}Qpr-F8^n9@aTQeTePH=uc7~^J>?A6SelMl&z;<NWF=9tEpGBUHiGp=25R@yqfuksSmTQALk^Qeh{@oS&Fjv==)M9Gsi)nLj9StGn}V0oTJmchWff>(D$XzpdL=2LOq;%H2omzQS@o_gQ!1bA9Lw5sOM78qaRK^k2;HfG<6pBOt1cCa*o!p-Wv8dmvf!P>ygFWg`C@YY@f%rRbJQf0R4LE{k#^(=}&m+{p^1~`_{URGX0!rN#B%OTN7m#byLPGm3^Y@BW2sES2CVMy`6pqwf1|J?W12ot^H2s>SHI<w4O>!C)0i)wf23y^0j`4b#y$DHko_{+cfJ&|BhE|GiM^TX5FcK(|4yH%y>DE@f^FH=dzP}3r*{fdE6wgV{OJ`=m%4O!1!b4Eu$?bpTwMH%+WrFEQhgv)R$BiXy^w#;y^O3E0LFAthGPm-1Pp`dA;%?c&zr})ZvU{Xj(U-Y2A#bb!%nSsXg_olb4{@yuDX$d-_QF64Y<8P3t!qd$jfqm|L2037$)7`a;y&7o~2%+-mftsiWBD(b`wxab=iSnz|aTj8{%6uec23j><YH>qOm(aYOo6<h7|A((5>uz9V%<)`_KmTUlGiTG#P9t}WwO)~w6^YLe^rX!3^Snzf*{WzBYswQfw^j=Cn}`i$FA*JE6dIgQDylGUTuZMCR%du8fc)FF&Rm|K;+IGOh4y>vdW_zfOYo;rl>#mLH2zd>G*aY3?T<bGbvWX*!qo<2;@smb}T!<+!Jf~*rj)7qfU!<+!JJT(1RfNgoG^<OS8UV;6YWEE&N$hB|irK1_^+``N)z?y|=S{GrPj)UlnP-|X}^(v5+qt`iQz2dTD6{%~mEsVY_br^L;=7e#qVPv6Rab5aQ>I7wfQ`TA80BX&KP-`}fvDOpl6UaSm3Uh{05A)*V**1fE3bppL=qFImpm)+QqIOd6AYaUQ7LWDB8<?}0+H;K7TgkV2<!OC{eiyaQnNPNrdKded&vqRjWxm$C8Si4wZrV2T`P7~~tq;;~rq(&xWZS4Wv){37*YQT?Yu<xx6L?K}(08WR`RjO0HuYw<>6|X~anwENb<L$bZXNXk#!DElW6dSh)0nfAdMVqqp3b%r)SA7|_H4#W$VM`68nq`km3$=iNG~4GHm%=fJdW+z)TxZeF(;Ken{zvsu}61dtgS1L=|b&c@m@TRtShx{JFn~uWoN0iKd0<Va?LJKYxX%~t>ZfQ<qFRIpZ+<^zyEA`AbS7f7T+WPx|Q`lvYASHwXu!skVl@QxzvC92Yg;X^^Jc4h_7Sv'

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
