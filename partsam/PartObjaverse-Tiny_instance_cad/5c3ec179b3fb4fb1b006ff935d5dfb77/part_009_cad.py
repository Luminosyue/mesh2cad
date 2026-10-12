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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_009.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_009.stl', 'source_sha256': 'eac688406cc368eafd83d6f2539bc953abbaa5e9867aad1bac2b648822bafe36', 'input_faces': 138, 'input_vertices': 208, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-19.52489471435547, 74.42181396484375, 1.4456729888916016], [-7.407709121704102, 92.99491882324219, 24.873395919799805]]}
GEOMETRY_BASE85 = 'c$}q~3se==8plWQfhLL%Oc8Me<)t7<2tLx0P|K4_K2S7eKtU{pc&VV+AYz7!3cjw29TG?plMqd`Wbzrl(0rgh@c5uYD_33>#jf5x-~a30y6fJx?z)%Ozdh$S-~9KtzrFX&oMVW|x@kuVe?6ojk3Etl<D*b(@xOUd2}!eOL?wF1zLU~KvLjA^+~$s%I65S(i8N1I=r%JdaYlmMK-q0@bf8-w*)2LQAt@muHasq2W|YB4M9fKy5<D>`;+-h**}b1nU?17fqmP^>|BrvIL<(B?GCy6kO4ja)ijh;oZa1TqA1op+sdk~pXKf|8WoabhTLw|Q^5$IPlGSwZ35b`1e(h<r<}q&)*B6yiyyi8Fxb7JOK64uTyw;1Z`+PWf!&vyJtBLEgUIx#Gk5uICLVo^(iEBRG@17XqO6Ng{?}|LNtQpj=6dC~D$q_tnh%3ea;tQWk*%)ua#~9aicf{BJJc0N~jMp;O74bLYDPBLhiu{#SN8;*Y&hwY*9!9I0Y>8VUkf-jsn7Ec?g}N2~K>kY12J+Dg>-&*U{bj^w9rYwW;RbPKNg{a8BJxrEP7~K>Um<Ss{nm@-vFj<~mH==qi2Zw)64&mcU#&rd&!j^1J0cUj3+kYrUjv^UUMF8(aHRfkWy0t8dA|xSxia6nlzgQ7>oM<pQiz-5N5My}qIh)_xUwF3Di70;&&Tu8?@DkzDaD7{>ywGgmrw^u*3oZiD0u9^Np$^&W2l?0jB)*xhB_xsLj5Zo!291uo-WB4mz^#09Mu=`wY)ECp7~PzdalEe2QLzz+elnr5{SCxq0ajD$HX<I8uRktiLcR`J^l(GZ?4-V*Uog^ll$=T*^GQ*6(?$g?|~OMV_cQVsKfDk_}H3|&*NF-BOkU9SC*kZTFrIh=GGU8OA|(tzkb`~OzrY&@OjqQ7w>lNLOySuK)-X^Qos6$7|LI5RZd*4FGBvc`zT(sD<E#UHU;_L3X+Li<%3T?0zQ6}1J&c<dT{UO<B1pYz8k*^<8r-&c^@6$kH)=s8T#GC^$)t;k@$%W<mqWc{<67-*1x%G332maaINKLniq?jig|J4`sdr*(|O+{_*kQ!+TF3lrQ37S?;WnEXBly&XAI((x}csLCu7}y9gX@|gDWjoV7}I<@NvL;(_TE?iP|z7`0S}cK7BHYD=V5KzU5Wyi}oA+=zP>YAF9vr&#7*ja-7z=?)D3DDGOX5UV{6Td;xq8*G>Mwj?VWuNnGFMfPC86Q=K*cO5*1EeE%>1k>b^-hl$HqyJ8+sZ=?O9)f^zM<YvHU$Rv!*eII;sdA~<=Ye%iA1pVfJN_omoYiYie2|F<^{{zV1^Cs@wxn}gcn(Kcu4L<pK=-2-|d}c00ovSvZ-wJST7T+gbvcV7W{h`AvR8PHCCVX6f#JCPTCx7L^0>lp+0G{ek`$!)U4Q@Gt`AW)cPyOVM#ki{Ls9#0Trv0L?8$(>{@;%o1$P(Ju+Qrd`w<<*4jz57<@IcJhr4`7(E%t>)bwwTO*T6rtJ3YVjA{qX3t!Z4+*B3ev@9Ts-vw7Zk#lAp3A9aM!mi6!tYDaZekF-G@<~5?82XkpXnBQuRd2#3cGVTfa=*Ml4|NR-r|3ee)NAvLOeaSzV@6UtowWhW=xOCNweplhSqn1_@x7c^Ye!01d=Ec(C0CD{So>P)rg)Lq8Y!`9m2(QD$5L$2MYInq+s6)T+9%@VRHV(v9ues>A(Sq@wXpVeB4q;xrasSustdRdraAm6l?my2Y#D}G0yg@;<FQnv0-o(dG#=3o@nC45%IY(TX!u2mmZHBrQ5tsA1o*O)yQ$AH$;F-K%ZsdY5j3%znjzd02Q?Z_(Pl101*I60gg6dG<LR@Qih2kyCao^BYa3!4Ad3{?OYJHvIf6p1*A%)hV8rBK%%WF`dm0PIJYQt|{#QWp^rZy>liN>q^NL=rB9QmZykiS-UjJRcbI((Kcq4h7%*-KpNydC|X%xFnmeH;Gs?;^h8JzCFNc@%sm{){@j9!~vQ7WaeCwx(GBrNd}_N_H;9Rj0m~mnC?PORInDLq4x=gnyefdLBtBcZi!SBax4_57zDebHt@ZJdc}}JRfT0)3O5bJ_C?X=RCakt}P%gD?Gn5Rf+ie`NXw>{Jc)TNL*?$hPY}Pg7sO#?>{46fqzq;-_WT|==}Tjy~%(3ZSaD!{=~oefw&%6h;a=w;XZu*TX1V9>@TYnf8zbWCa&6@MZf1mG4IYb#I+q?!N*g_{6<_MZoUj3snn+pd=3-0L{3Hg@VnSYdrA>sUCZ~+W|Y7Aa53_6XoGp##QWur2|f{A=hPkzRA;{d7;j@2#1F!ATrO||592ypEqH9i%UfH3mj&QHALvQ-k=i}=q;XAIjPdIBxS!|zL|mUb2zh?+J@!Re8F6{1Gy44|gXYC-E(PC`fPTGCG#dTtjw`{v8sXzw^wi+ex@q8Xdl8?L@EgT%3IZ?ggM9WL>`wWH|JB3b(w%kSL+$Cls*Slp+&t_l_~1&+<F8f3wYmp*Pk0m@K>6m|BEDe{=Eb>=?uX`z*2Lwp;QCH~@=?;ib0?qr7{nhNMC-@WtD3kawj00C%%yrN8OOkb_<Kt2dFoedwvV`K-4%Hr^T2!T>2mn5v*PuJbuQO^LR@Nga~%0J+ePa^e{UCYb7cVXxh8j|d?Jg9%clDjukG8&-)kPZ8C>a(`;6u`ht{)Y?G5lZEb!SDPWKs0_IJeP8{m404aT*woVY%y8?7HLG>68eM%fTIXNO{bFWvqdt<REYu9SZn?lYQg1HBJReYX<V!_H8i(nP$EX|;8|s17NO;QRVfee@nz!6W&-vA;d$aYqgKB5=vy5%+<H^ThQ{3i>@%h57O*1TPti^*`nze7@R3Ts{?#I!tR%?>UxM8;F}fI}M-S!>JCce-3fWhjo~j<V@U`F0Y0E^)v8s|AL-7TIwp|(&eq-W$ASPw0yN3KF==V{mrF3klL5Q6~D{muehwl_vl;g;J>31^V^y0<|V;@RWRyM`~~)1lZQPi|1CYy@3*(HuftP`O955L|8y4po*+9lx==k=uSNVte>^YR=Mp#fJcsz2H2j`0F^stM_EN<6(kNa|I_FIF{IVQ%vyP{_={-*o*Ms*X-Y=P+<I>3G#I?K&@L!Ne^^{UFiCdZ<MIGYsdxE?>1ODSJSSRzIb))lb(}|m3{Q=)AH(aNB>RyZCACLE2{nSw6<{OK^cR3)RiI3=etECoPZrT*zo3;mFosR~$Yz)M>?tG8?PenrygR8Ta!Ds40+DGP$WyF;t)LA>T-<kZA?#tw#o`-RDZSFzm;~a@g&o_e)4#E67op+*f1>!wQ+P)g^S1rKh!#a4zQ)|liOf_-k(lykl=rGks-NgJL;^l}6JRcvQgU=N|_+&=n`{ONeJ-ie6>}0BsvKm~vcN}@%iKKBU3E-+nHTczQ^gUO8;Vkk$i}z1C?E=>M;{0ypV?rII@#kHYkU#x;=-j(@`{U-~8@y0UsiPDf@rR!d4QTxR-v0Za4rjmgU;T9G>-T^Eboimjp-ku_p)jFgLL>P&N@$W$j8F=HUL>@fKL-f)67mr8=j)8?6NO@hrn65hdrV-DnMT=!Mhgw%HjJ+~`WwnVvD{w_x2uI#vB!M&G4fc(pS?II4{k@Zr;(d8=h~0GjXvHK3NfaVkKYlB6k5v1ZwU?Lm{&L^nz?a)9>*K)3ZW%J!5nAe>n8KHM*BJ+r?N*hA7^u)hR@sVIhl{A3H2B1E#%I}CeF)7sJ&2IZaedFNB(TfF>Qoe2z3?e_J?a;<a00ZHAZ|FA$y_jLVbl?g=A)~%sUC$acoOIXMFY)dP&HI&w28(ao&M_3=ePi@#dJ{kAs8)g<7#+YsuJ7@buw+U6>hv&4jFkng|)&$(p&*HWkVe+A5SGv{&dep+ceU{Mk6(z@Lq{N}(?~ZjMm0kjiZq`)ERIg%)$0#m6g!@`T=FuQeQRw43?7ac+xHrqFJoeL^1#eZl$c;N#Pr%MqayLZ7lKn0>(4trIHdYj&_-F`qlhu@!vY@Hr*4jbk@(+&1=E%f|*U5!x?Q%C-3mkLi%m8KG)Ef0S7sUsKAhQNM#ipYZu(9AC~c#`&`xbC!J$a_n)A-^}w<!u|zZy8`wxyyLm{#$3H7G*M^-*Lfk=d?C-lO0N3?K0k|(!}+>dd^}cY3j2){nj!QC$BbkDIQBKJN#@TgUl+%G2Ky%o4dH7IpLC%dp?8I53xx_r2<;Nmg^GmC9J5}iiunQN#`%pxWB6J{=v5&<q2b)V%*RH|06w3<ea_|Msoa0A(ECDZLZgIyg$4`l5jrfiQ|KHYf6hE#XcM=&eC#IFLCBF?C!u!i*GH%)w~l-qVrpX5(fU9AliNT4G-GrB=^x<!^~yg#ZvS}Y5E1l`hi{0f89j2X#DB)Zi8t<s(%%7STJ<d'

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
