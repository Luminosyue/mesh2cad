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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_017.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_017.stl', 'source_sha256': '294fe90dfface37c84bd8731a79bd396c28f6b73455a4a4eaa8c30215f859dae', 'input_faces': 544, 'input_vertices': 368, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49999985098838806, -0.29252034425735474, -0.19791154563426971], [0.18291936814785004, 0.20530785620212555, 0.19791148602962494]]}
GEOMETRY_BASE85 = 'c$}r13wTx4mB&v&q$+R1Tk)bI4>3l0Dv(?t5JGqaNO;NP1`-4f1PQ+Cv~#tcN;`@I0!C;j?I;35h0;z1I(m_SfXs+cptg!BEz)*?s;#v%qcVG+`&);7*E#cj{bu5~{QvKNt@Y2kd+(g=#8^_?_=;>V{n5>PU_<kVyc-QQ(ag*C9;{rtY~j4hnw-T;9?9}r`MUoBt{z`Du4H<a_n`M^kBZ8gc}siT73(o%{-7RxVm;<pFI~2@eDR#>r4^M{A5~seQ)%>?1?5XB&Fh|h2Mp>H>)WeO>}#?A<Hyxzgv6ywAG~fb{?e<*EH?DK{*Biiy<uZokM+L(jeJM<CQgd1uPd39QQxpx`*-u}MfcE?Z=b*PT7(`izshrcF3-~~!~gO;nf@u}Nlv_w;V*hTmg#?a{<ME;{GRmumCN4oeIGmG`)fVEYI%kptGvh8V|mx?i_*Q5MH%%C6%%~DE^qL@C_Q<iQ$~I2%3NPh-CDLUN>6-vX|Jm%JG6+b7hTsUc3nIgHIL|ep4hIFM<d@ax_-aju0uzo)>Cv@&$`V!GR{w|PwhTem-CRkwRT^=qsw{F^|HTGAMaBexxZSMc|_Oyt95z5qU-(Dx~!+@dVjSp`z5;GU#;tUy}w%5^XUE6x_-ZUf3+U0=caBM`<u$yRqyJuzh3UH`g}*1{nhodzfzxAdFiyfZplqY{Ccg|&08L+C$=9+Md``=mS^a)&e~se?H}xm@(+CQPt|^MI^&$+uXXX)y7-5Dlz*`A%0D<K%3pNtANb&(to`L__v=FZwJ!cz7ypot_U9ai{Lw@H=pldck^LRK$JgaK5bUqggZ)){u)o?z`ODXZ_7`3Ii?00xAN=b^)JD#)b@A7__=kLyzn)*~+F#Ef@{#p9`$**Z(R#2xN)OgY`)Gf4ezYF)SLY|>gTMEAWqRG@`&Vw+epi?0TjKVz{rQd_eE(AQ@_du}*u-dm(Y3$m+Fx|-A3s|j`TWtktdG`ZeL_C0kLddOqjl}CpFbfVIiD9wBcK0T56-93gY&6<l)rxdYhC;6=YPmY{3q>s-~GCi@26T1?n~(Uexh~xel5DbpJ-j~1ETBuiPq)5A-cYwXkFLq`-#@|Jo<j3b^U(z{Y2}*{Uo<Ga{aZg>qGZLr3d#V^w9lK>A`&rJ#;@*dT`%E58V%yuIoehL#69^Lia<Z>-QVFA1YneGx=P>FZ|c)`6jx4zKO1%Z=&nxTf>DBk^Z7<f6=wS=-NMZ_R=YT-A7-&$DiZ=-F|&Y&#9<)^*DOn+M1nFdPDca+g&|bi2mr|?fDUU-T9iGuI{17r&rWR>4^=yGv@aWo|)>u-*uVuc=c&LadYN8-Uf6vkM|rtYM$iQcUSxCtJcTchOXAf+lf9cbN(c{$NY(5%TKxcD?cxYu7AD|UH^O`y8ihhe!MhYKd$)!|MMRjejr1Ce#tJsA3cViqTYLWxQ~IpK3yL}kJpz*o}ZA;`iQR2kJjb<h_26%*5&+&uFsFw<@^M?IzNG~&QGAL^AqUm`~-8V^Apso^AqUm`~*Jg{KVsbJ?Wkw`F(=u`u7i_>)$_!u7Cd!`_9E<QTrRxnO}6h{#uvy7hSJUP_Nb}(AD|`K5BiuoPx;tLpuJV>-n{wQ2u)UpkB=%=xYAJM?W8C?S3n2{*aEp=z4ywCzQXQKd4vp2fCU+@X_o4V&&n;_1C(r4|-_*m7Y-kq4k$~z5b%>^%oyCe_d|v-l+LQI{u>T`L&)<{(AnPUd<oqYW~1S&7XX@AQd%#NXK7vJ-^ly%3seP)T{XeUCkf(sQF{(-rW{8e@K_-1A6HBqx6LG4?TaRUO#_C*UumE(dVbh6PqH>kJe>>(L?7)=?Uc@IzLjc&yVQ({D_a5KlSQ~ANYN1_8;=~FE{UgJwk8zxb!FfTr-ZZ_t)u(!ozO8)}=l<C+~4zKhu4$KgSp8daWm^kI!uUnD2MAD&^K|JyhTJjlGfe=u)3JUp3mkjvs$1qh9M$A6wCWWq!ox6}=8UKBepLUUPLmZ$s0Vucy|Qt;vr#Cm~(#ndqT=veJWlGJ5D9EA{#wE4seNijO)c4R6gz&#CT>-jTGf@1KFL?w@rVQ|qJFQ*^zaLA~0?pkA%B_wt$VM)`}b{eybtAJpr8EFbkkl)vcOKd4v!LA~;Cm^bysD1Xtle^9UdgL>s3Te5YF>o4bD>%lok51n(VS6_Ep5Bcc*dZ+uF{yAyU`APqLH7z*!dW7!1x980az1{4m{m;{NZ)Sb_v|hJAFSGuhZL56zL+p^NC(+}#oj#DEcV4^J_wQYnQSWt0>vg-fWYl|KJ@tH4eG)xXpOgAt<UHtlo>cXjy2$stB(3ZB8y~g(`{{MgTu;$stY^cA3nSNG>z=OfO8u|)_^-8|G(H)++OI%Y`xWRnrS+K6Gkm(I^@i*AX8NoB6<zOdpf67A4LPR|WcXC4^~CREhg@BshoD}ahd{p}t;dX>;e+1Lt1QD`pP!&!ou5E|EUjyQ@A0%A@>l0A@KNV2(EF$L(E1EW>w10k`3&mS`3(GP(z@Q?6uRDDeV(<h&vSfCTCY>*Q}l#ApCuW8J+pP-hC;8ip(d{Kvc37`?w`(drVfn$)0u_+{-!^j>EEy4|MyR4cAFXYnCOw^d9NDWWuj+R8hd4>xs6`rdy%tzxZwpRO2KLHN)roB6ocd7k{b>d!xz#!4lHnb#!)j4eK<bT@R&w_CHYZk7H7iC$rm}Fx5&vAfJN|1dW*qPPERp4#pv?BXW}uF{&Mo8(JUt5v&a`ZpSRG-jRFhd<@6STqn(~2YKqY1eJAip&_9d(7&MC&@ag17I-hr>lN$|=gwLY45FF$56jD=&F7LYnj|%#ylOKy_aRI!H{0Qgsj&O2gz!C82^o|6_Iz1z)8Hq0MdjTE`=(l_rH4~kACX%bd&*FIaM5j;Y8Ai<l>SP}28Bfi4^kMk8^Hjm()Rll$a9h8KUW*gpl8b}G;EU*;;LI;Q6R4Sh9>=E&k1F~tA5L8<xCn0R7t$+V?{OzL9E@jO{(4_Toy;#i?$`T-tjk~Ti||-PzvWX++-+h$crScDd@6XiQ#;4RTyQ>ouH!MEoYc-UF&mr<pY3?eB`3A_n3w_1hR<+3W|NcJ`%Fv$XTYa89y7>UK1tPAJN4D%tI1hDS?P=6li-uVYWP&8-wU6t)^jnuiD$pTdEOP^SK#)ek%?=;uJCK&x!@h}T=)X;UibzR-!t)J@L%9Rh93d{9p2Q$H72eEuZCY|;(8NVU}O00Ci;@^OV09zChjADA34i^V&bPJz6<^n{NGHxP5y0imRFdVZ|@G^58&T7@y{kI!F%A3ny4|64-SOq!}Gua@UNO!O5aj?EPn_b2o8o1gbx7kf<K7YL!fw6gM+~l@WJrAz~S)4cvXYqVWZf@9B>4DF}c~`9Js9+L){qsrDw8<sbDdDHn}O_RJg5~MBOC3q~~rE6Tr#vDdfh36X3RH26Z#=lAd`c3c<VK<H?Nz3*okAE_HM9k{);8=fOvj%LDV_HSG61a4vj^iGC&?2A9Bxn&?lyKe-{~Y|SI!{cxKfWMUckFx>XuN&Zf9{m9vx2f#<*HXk=p1ulcz-eKg2ksCzL)+_=afX`Guqv2If-r_8H5jDfWIJ}hCGr<!0OnOVfGWbMliontEvAiw?r@>3<9Se?wPp4)gSOPEL^;j?gA4_imI1*k?&2(@Yd<d@#z$NekdWV2R;rCNh4kq9$Ogw4g>)_wPYfY>-@on%Q;VXFkBv=c#@f7_QzXrE8&(m-5JMbrY{S>$!ZsTeCE&e^+);veQ#pUp)c>Of^Jp5bKtOcKg+uTZgEj|Wct9(|%zlqng;99uNucqJPH{j1wvl3hle;lt>;InX>Uqipee}J!|W;M75p2X`Ja24F<*U@kB3HUSAtO3`-zmC@m@EQ0z_Vfwx+wc|CtOIM|H<*Z-XaP2Z-)iDE6P>^=@Md5Ou#3~%jl9L?aNC<hoyE@Z=3q0hv(tMcd5bOKwzm&;7CXXQg3ZB>@b>WDU>~^k>`tG>*6^0__FzYNHrNyF4Y$2LsI}M@-Wr|_ibospX0RvR_V%LIVmo+ScpFeWT7fr#H^Xi3E!0}<0B;9x1&T)t@CNWE_$};x2e1>ogW7lT*l1#_iPyk-xcz<1eiJW&+u)Mh2)+d0PwzHxtJAZMnr-MC@u|n7o_@<;FtOdl&%lH5e>HK)#Eak#xa3{{UxXi`cL%uL>DfWe4)hoBIf%zW`Yk_d;^!uQ0lo)+*TnlK-T_a*C3h5j2mU_2C%~UOJtwF+fqoR9_waa+e#;w7{MN+p!1M6mo48=&*Wg*W<Ql+V!!OW#7W}Q#bC#O3=neRs$KyQxmVad8&nEr~eh&Xn6JMD482l72xsSk);a|}EDfnln=TmAvMgIt&&++)2e#`9-8CRJ23fK&Om5JsivcM*A$$4NFyg9v1z$=`dCe$=R_wZ?kM>F~@kD0j1#P#5f@J*)ehbB_s0r*}MZ<^Q)z5<urCU7(SO?qDef9UkQLd`4aoA5b+#{v2+-(uoNCf)!K!}pnZ%f!pzPPpW@fG@+}qIW0wBd2F4H9OI_;By#{!}MEz%*06(zXVUie`VqW6UV_*aLFA5kHbHp_Y`>2={ZHsDfDCboW|oc{g$6G@u7)7fEVHaVd9S_egmF^OYRK#8~7jTJqLd1^qiyS9Qql2F5+>Ke#<{G@fQ>S1%3(tZxfeH{0aOFF1b&@Kfy22`x*Ebr{^<jK12TmpD*$Fl77n@nKON*iL1dD@M}!8G|?Dr3YT0Xura(Py-mR@ot~!DG(~TOPYXO+&~Nz-CT=#-4eSnYZ=$1#yTGCF!6x!dbO1ZSCD$J80MDbh6WGz|=|oK@^!E4+#bYS_mS>x2Wui0K2HwR)TNCZT)^N#XgYDpL>1_?Ra(Y@*(;7V+pEh{3p}z|=4KXnQ90<>6<~zYb@PXg}a1dP9a|oCZzr#dd6FJ~*@ct(HnYbOyh2I9|fVuEHsOt;%hxaydi-~K&>)^MV=wqU*iIU>1M%j)3xBvC}@<%eu{@eW@v2|zWe|B;^^Nd&UAE8Q$o7mrpd5z3J{tx{2r$X<40F3+?{{'

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
