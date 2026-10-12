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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_001.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_001.stl', 'source_sha256': '61bfd66011bc9fbd7e03b4dbd5335e6fb635e17eb9a453ece7849e45355ea87d', 'input_faces': 492, 'input_vertices': 300, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.14501577615737915, -0.17666974663734436, 0.22053545713424683], [0.21100151538848877, -0.02181454747915268, 0.3753906488418579]]}
GEOMETRY_BASE85 = 'c$}r136xaDxySDeiw+{fFzhqXEHVp=AgCiKwu&eqFe-|Ofkqe>*_WUKLW`ne^r4byaBU5HBmzbvnmjs#pu!B(Gwg!c?$IO=2mynJq`!NA)!p}-dgr|J-kkHD-_O6->N{0+tE%rDO9s}eo#S{vZJnGcBS%DX9Y?CZljF=OojH5rn9^BYr%rz$!)fT|@?*Gc@a=<2hG#f)oO$_UOJ|Llncpjrf7Q6+{LX>=anokbo;iBzsA)6DmP+1l^yFEkiG0?C(bG#4|6I_cTer@E9)+C)4+j2^KlKu~5RNY`yC%VCEN{ow1mjy9?YSl`53f7E-OZ~yR@?IMz8`(pM`w?7^T_Y|R@w6C@uPcv`Jy`8ZJ!&A9C=^zP~+>WZFzjzXa3K<eZ%{<b^=3|xOs5;fNERrTye;EeWdI$H;+u79kb=pUT^O6<%`F7?F^b*Wy?c%t@Z!DhjP4jmOfEs%OlN}`>uBmzOv2Di^^iQJUV~0?|y<OMtIk+pI2$i!?Du+zH$6+n45==9E#a;XIFn;`{BCJl}R2b55%nb;Y?rq(a3N&cmCZcX3IlszVx@h{n#Jf@j5bOw>97LgRlKa|J&R=x}&(#mOFhP^IaeKy1ko+e!H;JmIo@v`1|LQ!BICano(iPgV~b~r04Oh9b4VJ#q8a-Jo>`7zV_qi9&vMLd)aPV9`9S`yFPfj@gLm#KlM$yEf21L(|144-&XzJ9rtr*D{Oh7prh~l@chMY9vw1xw=EAZ{Lz0ueI{&i?|=7}a$6qEt*)@;f&Tfv_M@+kck^gw!vnTFxV)D=kM8i_|L6gmt@lr^@83CAu-V!_<hp;N-@Ny>t^ZA4qyIl0@Rn_SO|Hk+*_-v2ZT^_N#{5~(W0P%unq1G%XrsqB*yg{<_56<xDBNIszD%y4ujtAz*V~@oWUijyXz`VAxb5imfn2W-&g(b++PzP;{v>m?{y5peHEug<eKWaU-<&g-xVc_GO|I9^$cPTB-Rsr*Y;wImM~B|L(#`eyPp;Sh(8@+D-1}7fi^=u=64)62mD`Tmzf7+8ui(PDZm#!7lk5F4I`-)6?!49KgkD|TT<_N=*ZXyF<C52G?F7HA6LIffogYlD&ks(AvKQTU)cM5Z`g{^TQSw6i=f;a)^YSOhd*_D@gR0Z>_{me=zFGWCReBzs)Z5!P=X??KU0-mmx8L<1=*!J|6<XJSw=W+v%w1<f+0%Wwv#8WtH{ST%&7Gkey?GTK<~!$@JaDGFcizaot=g8ypNRRck8UsX&JVwQvC5W58a%!?JrDM1;GGBNpN!e^P^a$ueC<SAdi^kMWXzU_insf&kFPrE?x*2NA644&$caAt({tx=(Azf;<y6}8c(3LD>&x%)_O;b3ciZyto|y0Y<o<PZq3`<SzVpr({`Rw{Y__&fuG@ENEq%*+|K$4q15baq!PY+}*ZmWDr{{WG|C?O*fB4wAwYKp!d5!U1@$*&I`9rSfPx#XVD{S-A<a&OFwggwC&+}lc?lyNm960QLUvPqF_NM32&<SszFR9+=yFPofH$OjncE9iXF_(Gs@bPX3((_<!fji%v4}K`O<?(GR{nxke=bgLSO)9tMO^^AnXI_OL>gBuM%&YLYx(Czq$h%A4wzZ$kRr}$qt2f&2-{kuKBb|48`){AGD{Q&$pUCtN-0^juY+Gr|YxHyR$L=~G&buXM%k_AL-wD0swlltSl`Yrf?kqd}ygT3ewXC+~(NLD}`tVbCJeNMNLWMuu>Hhn?mv`9m$o$DW(%aX$Y2V~#ewzE&xw(Inn|W*cN9U%0lI<{`P5<lM^nbD)=D8VPotyDZ_Jf-LIydttnX7r8Y+udiWWT9-YjQn5lh><xn9S9DOMb4JSIPF({4u$nKRVartLIPrniXEI&ky7^&JW}@&JX5#eSRPhY-;FzKke~SrSJL?_j>yv=LC}n=icw`Ysqtk`CNStF}Xg6kn3|uWM$mze{~Kqxju*J+^q8^*XIzOn|;LO`W&Kjvri@4QRfhyn|;va`W&Kjv(K7bpF?zR_VHw{&LKKC=Y-_%rOqMA`&Z|XWIO5{qI2E8K8NUB-@iVG=v?=YK8NUB_rE@e=)A`Gs&k0W_59K25S{D!S>qh?!dKSk-Q@atH@SY^lh>=~-Q@atPhPK{ca!VqJ^8unc~9o*c{h2D?;R~Nce(5u_r0ezdH5fjynXFR=W1IX+I8A@eLTO5_a1nDNtG>+6z$oYp6mCzCfDzEb#A`5nmlypQ1AMe7sqUQpx!I{e4ne{)9T!OPfz~7>OHE?&3guu2XE-+&6DA)E3Nt2A^UxwtKOsP+`K1AwllWeoj>7z5AU|+f!d$@+Sl(zb#C4ZC4aA#mwV@g`_@(1^7y2|2YlnJ-gD~QyazLRq~Zr}KCkUiVap@8KI3a&zqi!6dGD9(2lL)?#+h<kZr)EO`&qr8)Oq~aYXAMH_mDc*_Y-Qk_ifwnYjXYj>i3E|*Zt`%yJwSayiBggOTQ=7xt<TvqN%^J%{P<l`KI6d>0Hm}_^P98Y|l$FSI>)n@27M9JnHvyI<N7(-!<6X7xa2!a=o7D_iQ@X>y>`bmb^aq&)$15wSJmhub)o&>X*H7^smp!T&>SeR-c!WpIhSl>*j=3g%wXXa~!EGC&w8#I_*!J63UOE{ZE?{d;YKfwAu5@OaH%r+I%l@5AP;w3?+UK+=AbOkCuLb@4zki=kN=-1^)v7626OniGKy(!@t76hQG(Z#=n7oz`w!&1pgcV6aFpSihqlL2c!6R_@629KT_i3DDhIb6&H@h=O;?$$6R<NJ~>fM5_K=U2!AM10}}NxEWu|aDv+pIup>SxQ9BYf5x$R4#K*%jd^|n@Zo?<w_rmS?z4&DK0X`X@3O~Z9;?v<Sd^$c8R^amzwLei0z`ghb_<gV%zYqT@jNw1UXTjb0EPMw2BmMOuoPvLd?}XFvop?E%fzP1La>i1|^nTa_zaO6iFTv;FvtcKEHa-(xjL*cU!!~LC*@pfWwn*#$7HMN7ZsyrVjI%H+ZQRAj!}FcgJQ1G=>p7`;RgeA?HpD04Q(#kk3O)_C#HZmiDDeQ})sgWOc1{~#@%vymCp90$AAmib)cg^j2Ycc3@CRWKe-K{?`{4`mhbVFLe9E)A7~X*|#vg^l@JI1S;O+P$_#($!A7s6_0WQFA!2826-X9+V7vYO&a|k7V3nhLh9ERVC-$jWJhj-w^@mpaDek(p04!{TFH^F}RP55;%h+l_a1$*IF;g`dnxUd_3Io=(1#=GN1up?fCcYp!B1Kt|8#9QOdVN<+0o(&t~*?0q34;P+~H^9%M#OqMvbt&-+VHPgD2)__-1e@TE@Mf?D-VD!!ZSXw2J-irij~BvDcp=^uUV;mI;9c>{;Fb7gcyD+O-W$Ib-hf|=-w6BTH{yff5L|c*J_sK{iT?!NiT?y21@FQ~;UnR2d?bE1ycNG29|{NKL-Cv8P58}tUw9qf7w-eF!u#OG@N&EuzZ7=IFU1RB5nh0|gB|d8crI*>=i)iAIi7>phuL_2yf$or*Tys9d3Yx7z&cLqM?3@8#WV0)@It&6egSNRUw}7;&G5!}E0~A3!rQ|3cw0Ol7UKDM7uXf=f?okI!>_=vhQ0Bt@$2EW`1SZecq2X#zYPw;g(Gk|Kgd~YHmr0~=MC{Wu*ylDPsHzsdz{pHMtm;ZhtI|5!vpwyT=uI^9dDoe1TMlq!4JbQei%Ol7vKwMQ(T_em-#(^#@IXs^YN$frLYUW6n_R@fj@&UgID9r@L#~|@n7K2!-4qo_;Pp~z8rrMj=)FoyNDMiCimM3c7ngdrNoO8+>l_C1UJGKxRm%Nn1@S=zXjXlQsTdb1-O*>W>|z5aSxmMT)B@%@J(Dw{6hE}TuS^rxE_}hua)461pk((Rq!A9Dtrz60bhf!ga5|Y;cq}``wh6BT-MT`JKkC=e9lR&z2Y~+UplF^T6`#c!AY&{;&;QBoYY<*J`%p-r1lQ+QH;6F<5%G*d=%HbN<T=y9D}dp$MC<v2>uuRukbbeulRBJEBrWqDp9{qRA!=&*1~g+=ThRU;aPk&z7n3oPtm5htoe^Q-ku<Q+)3>b;yG}MliE|nbKw(CY7Y``2cL9OdzN?s<0#|$EG)*K#h-?k;!orM1q<*3+7y@dO4ctqzsvVi`TlSaK8PR0KZXnOkMSe$A^Zq_6h4d}#p7@>9>+g}kK&JVZ{qS@RKAne$?!@%3&wCM@%peDmlD4S?!~3V8^is$lz20E5SJ2f1wY26#M{6lxRiKXcodfszZk}GDe;c*Gh9l%1N;=15)Z&na4GTD@GveV-Vz?drNo=U1GtoUHr$6xi8p|Ia4GQ%U==PUem<<krNnE)3S3IufxB=i@gK=P!hgiShaceI<EP<v{4{<NZo^OFCtw+V0{=UFAOAak2JXPm;Qxdl;{U||1$W~A!ZR{FmgD8j_Y6wB7FCD6r4IAn>@`{JMOn;yvp3ae@2bzdH+z|Q6WADUg13Op@D_L;Y=!6H?O_|dJzfCY;stmSycjRSJHd__sk4E2A?$z`;`uOu=i}{QYrGwv3tQs3cyrhkZ;t1{Y&-{V2pixH@p|wAydGW`o{!hXGhuB!6F<lE;Na(Y4$eZE_h%{bQ}BEI6n-3@c2awyxa^rF12ZynYW+|Dt5WJGEcfC2AD8rh>Hjl8`hR&e(N^-00wn|M$ak8=m!eGf#n@VT)8YIFH0IK`'

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
