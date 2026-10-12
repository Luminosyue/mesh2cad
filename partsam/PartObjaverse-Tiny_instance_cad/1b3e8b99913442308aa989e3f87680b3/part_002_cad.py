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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_002.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_002.stl', 'source_sha256': '37a4e2ff5d1e801542208ab74a362b014cfbabef9748c3b5d7635168d4165b15', 'input_faces': 336, 'input_vertices': 218, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2115929126739502, -0.3247441351413727, -0.408896803855896], [0.37315690517425537, 0.04083918407559395, 0.2431592047214508]]}
GEOMETRY_BASE85 = 'c$}r033N?oyT^B8_L)MAp-!rV#1JGA5^Pfq`DjcfYB)iViWm}OL=S2vh8RMMLyQq2B<5ikiHO7$64Y==Q$ugHl-AJdci!j!cj;aCuJx_&p0(cf|Lwo`Jnyrgci1~;2@EJw)LFyFRa;ZKwZkv=OV!F~&f27q36Y`0LLwT6kDKbCRS;i&-f3))zTE?Z9JEPVl-ux-h+z}lTAAGZNBFumG`Wo!J0WsHaQKk16NZN<|I^^Gh!DFUF)Dami2b^Lv!=ccP0brLG)0^K!%u0I!?eohPufMlTH~-%)Ar`qlv++d%2I0NCmm91`zTs`qhN~oruz=Nlxpr@UzP6{^g#dK3lc?FT@v4-wH9ChGx)e%PfA7nH}&8jU3yI7Wj_^Po9|5jzpP5FHGL$GHuTqX^1U4YBa)AQXZS}SiEmyIDgCttvye|tlK6V2<)C~o;fTc7f9-)dFQax#|K4%A;s-Q3hx<Jx@r|a=dGhbWJ<xx7%n2DMEerSM?u7nv8zsIeawG2Rbt&;}4Z0?xj<w-?KF<_wJ1Rlqh6TvDCQE_%T8nw}+N%5Yn<>8K#}nx9d0TuV^%DGAyWux1u}Q{xosT+1Zx!DtH3|7I_zB|{--P%}>YtSUe(`c&#wRh1U)PZPvW*kpdMZqOz5Z?F-@mxTG0&@j_{-MGxaRB=sPnOVXQf|<^)ipfy>*D+DMx%Qc}kSZ-!gs873o)FKl}ro#W$*YNgVUz+2Whpmy<Y_!@;Qk*eUQoIVE`-{_`XsYln&A>lw|lZeImT9Fu7{{55gwWZV$c&Dv@h{6p8{W!x~-+0b0YH@10V9bQO~I7a=CkY{1PNY&r;TP@sgkBb?Y*MZ5>zx)x2V=J2~zCO_>R>t-AK>rz2#5b~QZWXN(fpNR`LI12<t5tvfW}MW=HnIcaPt9H`e%UIBbMp6e(WzO-u`jAh9c(35h_4O&ZjfA?b0v=EJ4JkR&4A64e~vrq9M&Fw>VgF2YwZiMuHtH^V}AXlZq_o>P*2~2GcvAg;VQ|e%>b<bE+@pdTrD$8>RCHm#?^;66yN$?<xR@B?Rx{?|Ilgi$2X99v_<}vFL~CF5#Q{5T6|NJTjJXqjXI6>IY#c+XmnkC!>b?sZI6~n{#oTw|HakCH+JXBJZesBrN3#$m{W57GWc7$j(sZY%GQ6KTpM>=$+%j`!t0XX?3wV-uay06`Jy}4;m}Fq>z!jHAKR&Z(%<-FtoY`;S0#?_Hxm9sH}Ngj=hzn)sv-WNrRe7qjdgf;EB5KZ(b$L2V`N@TJ`p$%e;S7V#ol0@#Lg7owDmLeHzJVl!s)2nHW%@&cOPz%dHk&z;*YH@``>auP43J3OE&K7^$V=0o?~R4SO;{G`L#`6gY){2AF&S8ym8K?`(ZwIy}|w(Qy1q(qwjH_)22$EnyZ8OdbN1*ZJC|rzV!BQ@f?YNb5#7}n<P*D$#I;|FAvLpwmqmT`4|myu?}5Q#kUlH93$h7P7~icWdC98s}7Qvx$mqSa$QS@KYbt0lLl?!fA;ne=KH49L+f-|e9a>ozT;O|hXwn^*W;%h5dZqulCKed34Y^A;u|hr;#*!~T>WHE@vSdhurAtW$-L`l-4G`=T<UKuelGK+dsa-7>*T?x>wfo}^1aDfsS@`l@-kLLA<wN##J47lI)r_hDZcGk6Y=%_Th>V3Mh8oL%Q+9kac(Z->W)<<zJB=aeu?YdN6ssAatrkDK3aV3A3tLsRc<NyYx95GhxxylB=w2;PJHw06!C2tpNns7uPgaj_9cmL4SQgf_<3f;e>e_tqW5Ax2YE<7MvlMu#@QwEe6*y;N_@-iis;|XEc0c$-$>$HJzl2BxaLaI-<p3Lbv{xkzA5};te=kcan88zLw~1Mcz<}|iGBLRUhyr3g$rcg1?@tf$L5Kzr+F@uebN2__SZ;1@wH9v630@#8uB0d!(O>g$(S$e(}~Ytmjdy%=MRIFZ@csg`NXe<|9Nbv_&eL-e5m0ozB%#{>f9LfZVOnvN8)|b0N>lY6z5^@2=R4~K^rB{v^Ln+{x!rm?hKUmVD&8}@lC6~ljoM6cy+Uk<BED(eyAnB@y9S(&-#GI*e{c+i*GGbVY}o}z6<ITeoNk;Ecc^D&6S5E&lz3uUNxli6dAVzpW{)#Bq8p~IH}Le0@UF`XZY1ZF^?syU>}Y55nn4~`AYTIf1QE#uy7ULJ6m?0DC)Hb?;B?lcgl6iIx}P*Cx@WFTafs+L$9PBw!o?IJEiZCaT3<c`q!SmL7s!p$bDMp6v*@1>hFQ|AJt2)HRswPlD{nq`JWx1EAv;^MV@n}l6A6W-PK%~3q5yP^6S%Cd~46@SEawvOZr<2D_@ZP@ythjQ^`N2zjmO8_<Fl`=>M5-F6KQfOX57~B)-M#FTCG0i4xybEFAsYW=kB)$ll`H0;ZwA_Y?7LKdw42ak?!QU%!)o3H3-uoEI_To9mXu`_R30lE3Nu)rb@M8vO(AOB|zbBKrIF$Mg7jtn}B$r6C_%l8kHmwedOWmvRtsswd+8COt>SH5(_8kLxqkA^WxX+U>LATMulPagB!0WL)h@ruat7aPiH_j_|i#L;Q<|_?Cb;8CQFJ1OARucpo*an6FE>G46fjWAQ94zPZUG<nQky`ItKv!cYGZ`ONBs`*OILA#q|}!O!R=<7$UrqCV$eBYxSIsN3uQ;+wLau1Q`G&Z5qf{y_a(RTba3xJCL~UuDR+mZsIjH`nxpzitrvkFN_qAQN!{HzL07CcfpC7yiz<vo%xl>*o$XD-!Q#`L!=%z8i^ea~X&{Pe)<iU3`(x&quMYJnl(7El*k^P6tQ4H^lyl_#6EgrxxN*DJSu@`TpoX#}WG_-~sCMRcrWt;xO;-lM$y}+iM@L6VtVyWn3eqAL3s@-7G^FN*#>6{^FZzUb!gaep(0d^9Q5OT@GVC9DOYDjea9gH_r^|uLTsKZm-6of4!=BpFZM|BY7l8BA;g7lBd2nOng(y4Dqe;sK52eMeMKPb5XY*HLxD8ypa5@!HbaptX+67PaY+8wxujZoL;lB&R>?7_(t7W@%3aU%u8S-*6onp=wG-3_gg<->YzIwNB<U?{QKb;_R(MGa9@{7W1Zabk@(gfm;RQ&K7NSgZ##Dx_d8*p#5bz$Kz+jQbG}yMJZU{h>S+#oih3qIMLk~*!G7uc8vW}v#(jnCkvizHZ;<E5L-6--(wl7L{TKS@T|k{3mto#J(?4($^>ojbaV;@L^CYh$SSQw7J+UuFmJna(dazDQ6yH*=l=#NLiJX^*IIsGbLH}l5Wn8PVN%pm+&{=$&QziVJmg9tZ*<Bgq-foLLpM4JB{IU4f4Mn8CQSJuLrBm*CAI`hcEe7i|-dB7J*P(u;r}&nG?eadHcgw&xsK3J(7`NX<oMShBm*<7nbRgoKH(}f%_by;x1S1a5A5)|m`z1Uab>R7Fd2$E)`fY^x+Cc}bhe1nGfA5L#L%s2L<2TsvMw`hP*J}>W;h>o~H;PO_|0|nNpL!3azn&5;zIhPN0qyOVShq=wa9>BS<9zco<9Xq^5_$4m(pt|(9Zt~ad24HM3vph2gZi(1i+L<M0P8AXBgQR_{cCH#2m5H-F~s3{YxpE!|Ne9m`DYYG9ZJMwUj&>+J)KsgZb9*=r*9tmH$9GXEc2P<Z*#wk{`sA;&V6ytYeoU;R_`v}6Q+7ge7)uO$Y;~<$Y;+G+*jcP^nZ%yk(P_+xVe~9zQp@96me#)IxF>=5dgnp39N_S8*yIE4a&#98Ho3gg55X=ZtNG|+;lzSmkGtZw>*dbkMr=nySV}N-*HiV{qbY;|G5L!PtHBWIanX(|Mk`9+Xnva*V2kJrk&R-*#F7iN@>p8h~N)?DpjWXywm^vr_xZbf9t2x=FNTnzdw~Ow&yU_-lC{e$V#V?qsVKitH^7~C#c8CO0SVmkgrm2kgt;Ssn^N*<UDFFIggydrg$Iq0C^vIBXtQ`=>qab@(QYjyn;NRI*Y7y9(g`_DVyRLHpQ#i6fdXFA}d`?UQXV|rg$?oiX6rIZe~+_h<bv2h@3^eO3or*q2`mXkS|m7$a$>kWj4hIo8mpxedK+t;~qA}Tc|6@TgV%z^U3pByA5oLt<)HD4C`oRQ@owJoV=X1+s>vqjk=k<nKeqIW|7m#r>R%Sr^)B3m&xbJIaGt3Lq5r-IF-7Gyoa?&WmCL^x`Dib_ql^jaT1&2Wa@VEcHToWo8n{C)8y04`xu+zv(y~&S#l=zBsr6Ol$uITWqwDgN#rEvag=(De2il#&bGIU_LgXGv+ZrBz3rtYk`viyFPq|YHpMAyice9q$*0KQ+S`8W5o$L12ze_tk-U|>h&q$Jh&+c)aWr){Ihs7(-sV!*QD>89^M2N`DLzb1C!eEUqNbBCkuR_*K0{3*pCRvNQygz^UsKmmQ^+Z-*BUm(E2-a-SCZpCsA(LV;&1G2J#{B_KY1s47xf5v7de5tm7GA1r7j}Jl9y5Eke89yv(4f7b2uO0uthW9XwJvG{HOE&-p$#&`<=^rd`+D}olBlU{)$cULh3s5Lh>dy#RsW}$?xV{vD#~Df2e&@)7~oEn-^7G7p0aV7bR=d659KZVn=FevLm@TwLG~vxdOF1xdOR1wJy0f*`3;$>`rb&)yZwhov5FZJCO%dN0A4U$5JPf$C4wclgSa}anwoVapW=7Nb(r+Q0i#%P;wvYKyn{)0JR4>fb2_cP4*>wQoYFU=2Eeny}8(%iR{B`7jkoITXJ)9OE$$_sh^R%lDktsCwC|Jqz)k~9ZBv<?nezH_alG7rg%7Y0(m&uObsWS$$hEA$Vxkt`;t3Q+mSnv{n->Zq&6crB-f)hBG)6kQtOkIenNI7SEYVTu1c=LrnoG%7P&0B64gXDasCvmy{SIM*wn{?>PU7V7oip>7a^CVRv?!oJ5g(soyZ?i-N_%38&KPj8<72|oydOVj?}^Aj^rTfSaJ|Klo~+}C6A|$BabJ4NgYG}l01SslstkwfZB&VfE-8-AP17WQGLnX$lg>>vNyR2wKBO0*_m3DT$FR^%%=DsY>G=!9mu7~<)}r-<;WGOCCL@ZHK<PH8ss|EkH~e%9@GY84{|H2AGsB|J+&jbJ-IhEh}@eTObsOmlS8QE$sy!H)Gx_{$o;7!$o<K^r~}Bo$p54UlK)BWLhVNGLT*9zCbu9rr8XfqC0C<5lbt!2)z}ojJChYxqLw08BA2C>)83yCimOm7YVXez#Z{>_wD)I@VpnP%?fn_0xE|F*dw;$uZb)rK4h(Q`bT0CL{a3B`AB!ABAO6R!|M|_o|7`K$HyhhG#DD*Y5g1TRolo||%TXqLr+ORE{soaEBFq'

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
