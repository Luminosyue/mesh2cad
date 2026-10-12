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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/55fcb4c56c9345e0bb18738061aeb7a1/part_003.stl', 'relative_path': '55fcb4c56c9345e0bb18738061aeb7a1/part_003.stl', 'source_sha256': '6b66dd83dd34f0f6ae9e8176e1cbe38b1a1ba7f2cfe909d78207adb25125b340', 'input_faces': 428, 'input_vertices': 428, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.041355058550834656, 0.03427969664335251, 0.006088804453611374], [-0.00806046836078167, 0.1184261366724968, 0.31119996309280396]]}
GEOMETRY_BASE85 = 'c$~ePd3;sH702faS_1-VK@<cYAOt0V2qGZMLj;jcP$&XY5+H1{NZ3K(u_#heX`u~^NFZzhWogg^5O`8HF%S}3>(c78S}fJNODRk3oIAfWzI*P_Kl(@Ub3VUczL_`o+?ly&=02fUw=!ibEAyweO7*%g&S{_&#dWH(nv$6{Y1GiniH*lSG2K(w`<(u;F74U3N3Z^#nxbZ=4$GW4G%K}rB(=@(mZ@ox)Zyc^CS_%e8$3R1SSIn#8Dl19YCdsf#uJ(P=LXI1YMB;kc6(Z6R^)&DQ%<K4o0YcVfY#{37TemB=KuY4`y?K_IBlnkt2-CwyLdFw>D6Q&eZF8l@%YWRn0{7f=ev0ND^-rWc>MiGPbKr%sI&R5ewfRCZ2QippIEbPK98y|clhnq+9DTEOuFx+i^p5<EOGKfkCZxj%7y^v@k~G2<G7QHe3;98EbqF#*u|rtPdeq|GJnfO{+5gUdERCImW%wE%lz&75qUCK8+MeqxXjaXInE7l*yS8g@X&aI%j+@^jSq8NS3R9)@;P{uKW?h9U!jYqN6!?yczo#tr;|CaTiK6Y=b|6x+)qx!N<L3?Kj%N!YH+(eC;#>CZ7!a8x8Y6~kKR>om$RP}XA4|BwtVqk7f;XWc+z=YtmjZarMI1O=7aSUYJbYCbIEzWLiyj4<{Y>9dyhCd*Ei;NezD#{T->jn_twEYEysEbago1W58}F(i|g8TBCcz>xUS{my77%4?{cjx%f-54F4q-vxvp$KVqG!k`V->fewkk}e=+YiA2GkN%YWVFTA$42`ee@QGuro1F7e36J^lNSRe3kx#nT^eaopLy^{7BU@h&^_UHveZ{n+;CC%)-`;jMa`b#=B{p^GP8Ia2K6(c|}=4si4z>IXd34><P|YqQelyzlV33URC}$$4E#&hsL<J-2|{eM<DhJW_h-sEf<~<+&(YX45+2d@fQIE5ri))9eBlk9^y<(8blu({~5>;LADwcz&|ithbT%PPw?6H`&bl&htLc`R@BIe%@QNN?crh8YxZYd_LssO3rmY#M2ubaPh?YyWeo~Yib{HaUOrkxekOl>S2hZK7{(8vZL6=c|1eoAjXq9*VRxzD;{=^C)cG=|ENo$_Sla?{bRk^d7RaCyK8)y%ll<6@0WRK{ea8-ZF`ZwZ7=e-*A@BO=UuEf%a?z%Aeq~9qiAorXwT1u93SR#eC%^1=LOGoX#F#n>mNL{{+Y}54<1_o;Gy-;T&{oSa{Y7va{cproLv80$K?9w`>nL2#KlAFocp=Lc!t)wc(2SkINz+F$!)eLkEi53Zj#$`0(ksy2LtDXXq7nu&izZy{Y!4gdBlvsb?rI<=l1rTJa~+`-(&Zf=K^&j`r8qvefz_K_nLUwp#g5!o8Wd`$@V;7g7f&RE&a`NRK3~u<m<*R^)dG~w(<7l>q^eojjd?w^T>q@roN>unwQMu>;7b(uiKYx3vfQay*V^5na3VGXWH*R6X-|or}nyHKV@$B)1_ZcbMg3~;yf3R?jL9Njn7+}JUbQz&W*7a_04s^K4p00GP_(nKKauEXM4=MT2$MNXF+vSKl$AL{;dIS&((t4bG6`nu8z#^yoPw9^SrHo9ykv~2UYZWv|3eDm#UUE{cpPXl0W|Sy87+;oDiGVVU<4))t_7If4<^pg)Sbel@d?pi5q^G>-Y2Ju@x>Z`(b{ieqy6{mjw8Nh3oxsE1FU0;<0FlKtJ&T-)(T^6VET*99Tb+U!i@h#-2S+zUG5{E}nj9N!-N~PtHE<>}O)#qt5ncn-;lvWNhvU7w0-3>i=xl5*LrRxg6m3xf@t_uajqF?|1P?y??}AJl^lrVHeM-GwG;{C(4a3a`ylAHz%C^H=X6qKP{`&#iRE(I_=`Ifd>Pe>x`Ut=J9f6_q({7ksEh$Iq$ZAG4Hm$n0MxK-kHmJxBZKGw|Vw#U+V0q<4>I9pvJ8Ta9dYf4GZwZ+%x`osq~fs9!s3t<9hC*^?%s=-+1h+^5&dy)6^Ay|8>*W`PY5(yF4d<=Y>KSkM3y^Pv((oL;Sj-4&S{hnX92oHwJi<>wTW{d~d%W`+bPuwr<Pz)gH=s@#xg%uO;*JZ@<{*>YusnpLul5`}r;&|7d1`i^o3v$e)LtitjA<=cRa(sh_B~%oAJE%)ES9d!~P#md_bJ-Sfv?^=s$v*Xe(r@ALGneSL20$-EiM1M`daiPQ<EeaEV1{6AY|_T|^R`8+=L@!<0d9y>WUSZ4&c^+dMkx*@oI-oYaaVy6AR3p)awpS$w-{{R{HnQ@qz6{wTU`MF4Bo)5H-6rJ|RJwAUm-j7?E_VX&`B|oRk6LY4U{*Qi=@8a>?+yZC&%o_f<MP6=V#=qA2!2ZQNR&*(_Pf5;oNph|~mjAw-Sr6DZLmc1#ggDl@<h;&9?e`YvyLhz0kb=PdHkuvSN0{^c^8O_`?^BZVe!)EP-n_uR6YX8!a6bRwz9i@S3bjXlkeus7h~pe3IiI7L%ku#9*r6{1=N8F%pR)Z=_%?73VQ%+@f@AqE9-T3$z{PnTO3wRfsDJFIlFK~hei~|jh5UIvhw>NWCil}&p4d-A{a`;0wa0$Soa;uc!dv++&ikyL7qQRU{+oPe#<!$KV7=M>_rTkM{%w60>z27(x6FCpk(~D($$8%iaqREv@Ud+FzCO8Z&Rd&bH}#-@Zg!x5yg#ZsW0v{roZnM0U(D_P`<I$qTs+<{CD1;8<J!RfE;)}ws6C!v$@%%UT)cOLIDfC@&5I@97uU}aN1l>%o}u>0Q*zET#8GD?=Q<;KWZ9NCocZwg6|y~l4<_3;8dT)sIqUv?!r8w2#bRgv{CyX=To01-d!^+3UTOOm>qPR<_=|NSd1(B>L*vQ)%kkv)ay+@c98d7jcyc~s+~j+Gh>P_p_bJKc`myb=a9ysqA&&E^<@`Os%GfFwm-8;aPYCrR=H0eO-C(X#{<z+ir{y9~`@IBzzb&~K=lF?2^FDIx3-euE-mk1PAuj5SeE$k@*}mz~eXcw$7wf@t@w_mX&kJ+jUnJ-KMRML>LhZjEz2BM7rHyfCKG{PLyLja33rAc$=fwE8oc;9rsK~|Bzp7m9%%{uxQ%?Tcy(P~3`f|0Ks|lsf@xeaJ+`ey$b(Ki#z2CJSESGhFxvT@s#k@0@^Uhq(J99bj%;mh>_F~>`K4RW&K4RXP%Xw!m=iT-r=AF5mcbkuxcgw}R+xrspZn>CuJ3ch;y#jx`@l2QFKP=HdQlzNLYIsJ{Uu|51cC7Bd+BmBD|Ld<d-l%i9O-FehRdrO-aV_*}`06^U(Of}O;D4%vZsQv0b?~?7xLHRnXifO*b=;t%9JD<A&A4_==(X^b@R_Tj<=`X!Fq^!p!{4f-2DA>eHaz841^HbEUjcd(JZVMv6*^YZ8iX!}|Ba4p9V4Nm;3w;tq+<?r4g4}4zt)ipeHQ+gI)0^N9rPFQSvn@@m<@di{%IZ0=vW9{l;nruXVTxo|HjkT)3FsnehYLN{1*5;=u-GR_|4E?!Ec7&1pOuaCisoeCGZ>JH$Y#2-vGZJ`aJx4_+037@VW5opo`(x!LNlr3%?dV2l@;69QZZRMeu9jUxGdZ{}TLa=tB6_@GnB2hJO)$74#|iRq!jJ3*cA6uYhL5uYg~!V;*!qG#ma~J;z_^c)&B--ZTDd?Z44c#xr`2XFRp}675LadB%@W<}<HCsV(`x=y;Ky70+lPJbm^He4ez8XFUCxrQ;sxQ}AVUT&1HMg8WdZ2R{^kFjT=S^g(`=j*oO~h1T_qPvBX-)-##|{|~L7>$ul5+S)UICHh(n-3mWL$8;U@pc~=S^=G>37!2(W-&;qK{{6$yvYzqu*~jsD(u44$bxc#VhZubw{&zZ#==dJ`Cj3zyhjbi=o`ZivU*l07Q=voPCwS&})1Xt~kD#wNp~vCh(s5YFdFVgkDd#^TZ_=y1AN?`>OnQ}P{O`5@gN|D~qYXXd58-;}pm%u2AHhA}?iu|aeyY|fI_4tC$DotpN$0@Ry$!{EPk`?a9SPqbegJe7`~diY(9!S%;U9xO4*wYZAm|wQLGVBK%sL?*3mpSbHJ|p3XQ3nEyW%t5p=05n)DhD$8#))B*4%WoO^45d&VbK?pQvLJbS88L{87xo9atMQ_IKbKb8!79;b%c7!_R^rhqc!a>u(7B2<Xq?N5Bt<_Jtn~p9$>)p9wz<`Uw0m_zdWH_zd_d&~fnNkSF;QSnJh1qvzqD)B3!Q4baW-FX&jJV=Xifp7!Xa%Iwpmo8ajTuw0pQ0O=O^KPj`vm-CFSgMUYvYga-J8{p})AL8?*w|T~Ypv)Pfyk|5Qo^tpz@*s_P##7GkBX80=p7HPD-cmfHYvJkM-^Klt*7l62vqYvc=Lyn$c&dr>m8q9A;AcV?z|Vw#QklJg^eN~9_;EVM>UagZ9{vd(<8^F<u7;ne%-QH==xlhZrBpj!ht7qkJ&X39LTESmG0L2!wnG=f(^;!jne!Iu&7Sdp)A6Z}7M{_&J>x0olgOL&CeQd!bbPGiF3)IF&v>e_v=;vfr8P+YZDsa`8$F|OcsfH;ZCwMUno9mO#-g!j^kw)Gj9nwo=r(v7!&4YX(yE^E#h8OM&*&@gXSDuRM|00;Gtc<XwEw$~R-Os+Eum-ON$>HD{{!xg_Jg-^PvlE+4>Z1~kvn<Htpxd%Ab0X7kt>aFF>)k7T$!`WF6gW9MVMpSkH=tc$rosSO~(zM(Jr3x-E@4Xf9?VOSCapUXMQHF2cLn@41@N7r#98mj`UXe`}Aja>gWjF0Z-Sz4>^#35I@s-^54pwA4xAK`Hr6Xxg*+=zeC6EIv#@#gr~JmXB#@Rk<xjI{9a}1N)^->sx#zsl=<DYXhV!V)f=iS<xyX#&XA{iMs=ke>I>Bw@>Ex-ex#s|P(2|}b#9L`wT`s1XZ&vM-_Y?>&u9hDcxtm7?RMk$<RjYCJ9lkp6rSGM?p5a9j<hv=ZM3Na?Ep{juYHv1uMhenpQ@w3GVjBrKZB=#g*ZS*J!n7pvN|53H3EGYp57zdAg?yasRDAM+^&K4hNpMqcDQ~!TsswgQJ?jpkHXi%y)=LhfUl1>b)kLX>0P=luG1FRsD<&RvAq-81iqGznmXuv4$}R~_)eIY&d@#Zsc7E-S__```iDGo79i~fe-WR#1Z@CMycgP%zl5J3#r=1Nc7kuDBMtYNhB+Wl-xIV{=DPyYUhtmotFx#47Y))*@bo@Nzgq-V@QszJ>y4lX;AyNXV7y2x!gtUS)p0+xBRq{s4U8k{K4tv<%B=fN(B1I$(LNPg6Q0gUJu$95F;3(!;4>GYsqi#b>F6^Z*CXEqIk$yg58oEP12hWX2=|@_-4DMAWAzO52lb=xgr7TM41U088e*PE2f;rC|1dNi{y}AGQ&;F>_!i2XCGLjKhaZ6Fp)2%3c=}y)Wu9BoHt_W9(KDC=?W2CI4MTMFg!X_R3GD$t3O_ef=G<`?bS^waQ}j*xbNJryeV{|&sZC7BozOY(R1fHx?GEh%Pnru)`Yb$srin83i?kIyeXsV2GWCG8ZIaK>@qmtA-Mp(Rm$}kE)&B7hy`QMSKirm|41Nuo{K*e=U-nDUUfr&yc~DpB|L7o=M_H-=0MM!bPy'

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
