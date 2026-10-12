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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_006.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_006.stl', 'source_sha256': '140b5c3556ba97b33cd63d2aba8fdbb56fb60cb1bdbc0e4a6a17b09cd3a42762', 'input_faces': 468, 'input_vertices': 283, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2499357908964157, 0.1422221064567566, -0.14223088324069977], [0.15399830043315887, 0.42948541045188904, 0.14503242075443268]]}
GEOMETRY_BASE85 = 'c$}r12b2}XwuWl}uLO}a1QDSLIugVHlCQM)s#ie)L81tagolcXz%`&~3xXg)lqd)`QF59g4PlxjaR`Eepd1sDBuS8@_f*x_oT~G9YrXZ}u=e`D^RGSoRPU-&-F0Tsq+!lnsY3sh6%C$!s$T9}g^+QRNENSk?$PVHj-7i}eX08!DWahA<xiv|8a02SN$V8xs(3T4Q|F!?d!*HI(&}}ol~%<`>+*7sUOhUz)c)ljojObZkq+H@c8>c!yLRZ_IsW?2`)XCI;#8|x#p&bxAAj=3hv5Bkbw^fQ{eR!Lv3^{gThm(BH+=8;nw#Wnkz?bOEW;1*gIYDFnfdOZFLi!#yN<ZBbhCWzw`(xTtmEQ`BbQIM^3zLim9O2tBNv(ZV$(z0l;7&n1y-G^`F2V_cB;c-(+_Jm{8Epz@=|O3a|Z8G*L&K|kG<OKYc>AXc75?(<~QnnJ$w8Pz8H}-{=4t`R^{)%L-ir3-dp=!%4|{BTO`f$o$O=Ej}06%G0X5>{NVo8ftl|wyeC_YKi>~?%={2PaGT7t>W^!n`V%&~w8*ND?;Kf}ZstdQ^WXU>!^{_TwC^o#u-MG^_BK@g6piirK7Q=5UEl5d=U1xEP4@V`$ggjY-#_c9KF0>z{fT_1y4{~J9H4yvd)<HUUoUFE()JCi52e#AKQ`vX7phLhBh#`B-x;g@pna>)&3rMboSGMJ`j8CW_j=ovzL%+dx3I1s`CfK!wVwSYS)ZEuK7Lqs;%8>Qvu=W#M}K{l*=D|n?_3%`$IK7k?yBdp(Se0#ehl9~JYtcRAAK$kwoNzlqxp@!k(y!VyKSqgdGwO%d-!freedE%HIM!Vd;C7WbI~5Z*K4o(-1*Dx{zQIQ+U`#{wzi)4n4Vwf9|d)Nr>>e`$4Rq%_vS8Y9z$>I^ei(U-yKtDhMDhm&D8r<@n_Wj;PkD$?Yi~x|6BbiKe;}Ba((y5^IKGYwN<KqjP)7$-pk+X^_es0bTdD|7j=4kZsv!5i>Y-eewvzL=8Jy#Z?|1+<~!96Z&&Y|r|1eZKg9Q^Zd+m1XZ^(9ZMn*-&-!so6<BTNyKBnn&vjnAzK<`G>ieGzR`VMsjX%V9``F`mr=;yw^>48I<Ku@l?f$qAF4OtD_4@JazNY)|<^?^E+y^6HJeH#FYyR71r)C+xi|;HRKF!Sc9?h%gw^&l0g~#;$uGRU#tm8!fu+Eds{Mg&)^!|VJ&?4)7-@)%cG2P7f+jUd-$FRkj`DVUouYLE61q-Zkj`Vh@KD5}e%*>DByQc>%x5huesM=4&`<F7T@!)%97cDmPqjlmm{~<H$I)0G3Vu>|Q)=zMz*V6je@tvXLR#^S1{I1@AlE&jy(Y}*3o?!SPeLqURUi|QseZApqPwhW$E4!aDe1C)8Pyg0ZYJGag?D-1tWA7!+SB^>gKGnuv4*|XyYOe>saUu0w5$?CwtzTob@_pZ4pONpR+w0R=Qc|sd|7%?*_SdS7>UvZEQtMEprdhs!I9uQE&itwFzmXr{yYo*3R{lS4(f6r!56m_5L;T>6x%15Y*ar{k=ab?!(#?Elu=c%0zolE_Wc_$qyEDxEYwM@=;KgRXXwp<apOi?dkMAVacWdWW^Xsj*$L~e{1$+GAp}Y0GpVR#j)rzcFbqaUV`z_CVk?-%Sq@M>eHcc?|Lwt95v%t(3l{=`uc@@gcG4nlqx6QD*W`200rM~Y!{MI5fU!2sw6RVbP<<rk_eVz;}KYAW$w<g2PcaA@xKQBr3UHsTVyT14EA+^s3x9joyD{6&m{gj=k*IQBcN&K)*FTJkHrUqHp@x7M)CYkx7%U5cD3u-l*XXbnO{!6RooB6SG_v&@k^GLdx@0{0uEdQhoYdrKv<Q}=$%#Zpb+$WY;<N2kN>O(+%=lj}f{}UJ5sQZOmg69YP@bSk~A7UTpm~7=gq5WX<D^tvT_xF=(oroM~7MS@ye(ckk3$6UdhxI<+xc(9|Kg17@oL^#%C;EI{zIB;3p6L01)b3?g{q)KDda3WbM^&Fh`Tly}o4G`-E3e9r`n+{^tbVR8#dA2ms6A7iL&d<)rkeRKzIU<EbTi-oa)DkC%Q~c+`C_;BW2Z`HnEBzh+Uk0PK|PjR^|Q6_R;ZL|jpx(H^!yeXvBJv7cjq=(Y39eCJg@hY5A6C*Q|*W4b^Tb4owHP(H*%<bILN-D`WRdJnex2}SJ$cf<=Kbv#U@vuUz`Oq%zPK$Z&_xRneR^6r`DS{x71QIKg16o-Lurp50BN;&w-hZR$Jpau6_6S8?(&(AiBS|d?7URuidXJYz)o(Sf|(ZbKnZQzS~**;TgNWU*P;+-3NWW;n1xk)cbyNNZr@GT!&Yhz8HsJchV}QR~Pm(#}f=Lw^qH++);0-I-Q58*CLJc8ou+*G1Y%D`xo68d=KCI@u@jxzQ1>mTA#s~JC>XIVxRW?od=hj`C`y~eSf^IPiW?c`2NvvLu;JT{`291HD<nBEKBt*wtItB$HxzXvTMvb-pOE}er;cuj~^Vgugjg$WWVbFR{fkH_V#{Jz2CsCs?Wj39jgD4?+((w|K~u}e}7n;kCisBuKFCK&ygSeeVpp2)8$2VPK^9m<WD#-$IK6>jMn==Fm<_^?@rZzShsDaneUAos`?rGH9Iu(#dz(D_bRQi#uKgQ&#JGr@}u?KZTMO%KmSgBepyv+jWvFJztuZd{qU*Hs?V{mN!N?-jkB-UTkw|Zzqf_{r?_fg_vSsW`*VAm<%>}h)~kMu&YGEJ_%6Q4t~%SycSp9>`#{;^%gp>R^4siOX1(vt7xnYo>d{$dz9@iSB`q}bqkg)Nlv-ouN9V*MudlK4n~l@o4`kW(WB6WDeYav){XAUG9={*?t?lvq1s~Pxf2`e~0N>wY_b1lxl=9td-GBGNj%r=U_O;RLtz??z`}9qWAEdr7jr^#e!LC21n)%{V9d*C<&OW`!%y%RI!y@TszB_b)x=#tN_gZ~?pZU7xNByr>D$~r5`tN7&&a~=}+^z0Yeo}oOUnJER?Jlb4VdtDZeg{7omNb6mMNF{!6U|q!!|qS;;t{={e8cys=bP*OyTy3@xz3wr`9Y!b>OK{uoYMD+C?DVNwtcjj?|(mCKNq#kJ;lrq@WUamO*QjH?{n(;&>dWSrkU^Hi*Ud!Yn)O4U#l_O%#TIiug;z}$IOp;lXk1$OR6tAXy4CDs{g_|{k+l29)Ap9B#qx~+F#!na@zfgeE)g7KjGb*_2=$azDIrf{dM~DKTAJ9r=(fFJ7bGJ$5qV#Zq{{t@5<%@X1=$o!Y=i`+b$0`^L>1`#=a3|eyrde<;QOfqs@F#Nc*vYZ+>FtU;7?AbNpB{KkC0%zV~=D-`R3h=O@*Vd@refa9a;GFK)Iy{>b<5Pa6My+w}Zaw)+$L-X*&~eyQWikDcPY-+zvEy<R0<C)szeTt7d&tm{X9)Q2#s&b9s|<wt#RD%<&yFV5TVd(EegS96I~-?<piZ({uw?Y3s6E_W{`gp52QRdnfK{0U8(@+Z>k{|W86>i?@hp;fO@>;L;FwEXcg+#HY6=uL2GxD=WXE(MoF^TH+J5@;T{1Y8Ww4Htt`(Hr4ZxNtlQqPfr;;aqSE`ZqWQcF=OL16N0Dz}4YeXdSo~Tn~K!t_MF(NPZG^;V0qd=s)1*aBK7-xHa4!eFSa~cSIkBJHlPj25?vSc|!7Y=wtA6a3}O%a3|P9ABH`+E&5NmE!+Zq5N-iCMeD;-pMaafO$f=22+0l6zrzjTx@c{<E?g76AFc^kL(9U|;4)|qxC|`N8${wqa!#}moD(h(kMij4Xd(D^I1McVr@<A`qHsmHGFlw24Bv&`0^bGSjou314d0922Hy+chn9w=mV)nt??Fq#_rO)r5^z<x3R(=V0#`y);Y#qGXkqwH_zscy%-=ysu0WqF(BlgD1&D&oiPT)i9OYsTrKT8jD!B~mh{PI@Tn()*5^F|sO|+IstTD-T(Rw1WCM7pS9~X%=EIC@|k{hE>!j0i(Xmhw3+!AdKw}jiE?cp}?GiXQn8Mp)57486cMxTc}!~aD{?t(rCcY&WpJHgMw?NASH2S1Irg`b97p)KH6@Kb10SZWjamiR;#i$@8xBwQRVik5_n!i5RRMbKh!5jZs-e~U-1c;rS?;Z$;R6O!{1l5aw9fp10&qPM^W;X-H$IJ$;HgyaJ8$dBeji^IjawtR%-JZND!4}4=hZa{OQh2g?ne@;Sj4m1@`r5BRFjnBcpcx)jgZzCihh(~5Tw#H*~JibBqqFdp;@P0HK-Vc8lk00W3FdjS5@8BKqS~MG83$G$1uSB=PTN&R<bT+&ao{N44&xI!ul1IkFkH-h`csm|%p##wm;DPYR=ty`Zbv`B}Pe5nG6X2O>COi{fMo8X>Zib`2ZzLpt6^~!gU(s*iU*RL@Uib)n4BZbOgMUN6gMWihq6guV@M-i1SZWMD4WB~4hfl#L&;#%Z_&B-`J`Nv6zlD#&hvRVw{Tlri{u<tdZh@t)fH%R*3CXk2Iq)oaA{xLG;SurZ6OTdhcqbn3qJz;v@E~#r6Ou=v0XzzxOh}%G&VlE_8R!al1=p5=Zi6%6)r92j=mGcu^Rb<fypE8(6OF-Ae}H$wyU-o*E;x&jya-(jOI-yog6E?vVX1RrsgvOO@DxJwXmlhz8Xkgv0891ZA#mS#yo&ZheYh9g1AQCr0e2UPy`wuJ`K5StLwlod!M))D=s<V?JRJQPmO23*4v$A?!sFr3(Pi-G@Df7u26Q7V^(%M-yjvvpn%#utp9smn6OzxNzryF>3+NH}0(=oY2493PqrbtI;j8FL_$vGtdK&%<PD#;v3YH;RpeJA%lK;dz4*v;XL65>$;7jOX_!9hwNbF625R%Ww<1G3!dI<g*-h+M(?}5KSH^EYu!(YHl3CT0iS?~<_Q*<KyDf|&S0+u=m{s?{_?E}9LzZs7g(U;La@XPQk=sWN$a8HrgH+vG2{~eFl(0=H<a6fn`IvAEZ3LXlNK_|mw;HiY<1?W6jY6dKIHM{^$N4LXL*TLy<i0*`??t(*j4Vne7ffo{zr=g2rsq^7!@F(aL_!D?6IvO4e4?~B*Qv1Tg;P*sgPkfJ%{JPL*3aOpZS4HC7A-MzEOC-)IlAl3)h{U-@avQX}NSuQtw?tnOiF1?WW+Jh-M&~Ta@*LI(eF5zTzW~31_J-ep`=bNk{_uzBa9HYi_(OOc`Z+ufo{lbor^Aa0$?MS#u+-h~diYE9C-_VFM?&%$^mkZ3-%HJj{w@;d0?9X^=U^F<Z$vM^G9>3gFN(x@L~=g#vPhg?B<Dx3!ZIWmK>vbeNG^n?80V%G&R8kz(b1Vpa3+%~_vo8>E%_$&3M@l%Ui6Ykob@E<M*k3r^PuFvq32;4l5?db_VHYtrOwjt9Pk<9Eb}AvXJfv8W)7w9G3Im+b1wA@Sn5)^NyC&JsX70r|MHRe@nvtU{{WKwoA%e-=5Ia{uXXK9?<Ngzkl)3M9Pxj0!#*v)jS~L>Ndb-2'

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
