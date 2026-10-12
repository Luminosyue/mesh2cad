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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_007.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_007.stl', 'source_sha256': '9e7bef395ba46903d48037b36f1b2a42af2b35f89a27bb5c038962b964cd3c97', 'input_faces': 218, 'input_vertices': 173, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3125220537185669, -0.059316486120224, -0.2176518589258194], [0.3567603528499603, 0.4999998211860657, 0.17714187502861023]]}
GEOMETRY_BASE85 = 'c$}q~33yId9>#AZqKKkGEyX8jEV0HCin+C<T1zt%`}z?HN<|Yw(6|UKk=laT;)-3OMPjKSx0WLIpqOg&jkcpDwzg9#hPmhczv+bMo9CHlCZ7NE{_gvod+xdC{Lk`zLb`c+`D*f4OPh4-ai4wVG);w%=BveoM@<+V79QPr-1t}ztsH#ySEx&R_U;kV-$RShruvTvj}D9SZ|m@H7ZKzi;P8)#jG7QNY~0Yus1f1H4<0r)I^6c7M-3YvZeQ1H);ci25m-OK@uA~?{3~TQ!5E}n%2sXpXW868+2S1iZgX|5|CDo4snKZUIrweFH}a$4TR;5sg7O_t*Q|5rTUM`iN{xPFrJhQ?QID3|VRg1Uzkd2El>e|4d_BMSW%%jxTr24JT(t9QLJs_w#5Z@}fp1j4hv(|g`fYaSYkewhM!T+GmU_x{z;lg^dh4^@_^z0|)S~6}cb;5Q*JjM$HlUo>At}Ev5A87;1uu5z>$@`+;rT<B!?!lol=q73X=c0ejf<sC^moEC@$a>g=Z?C)E!&OnY>>JQ_w8sQ@B2%$Qy7=35z@~u_(tkQ^s_#D-v#)`i=9M!YCM>q?Z!76pH4tOjLL+s{k-@D%KzF^@+5wV_)k5rpj_RiyU_oK6X9FMcj3KUCG#@e`DW(93_Pbw!FfE_r_)uu*G-OZ?rQkfl@jpHB^%bc^BuhgO1}NNSnB!k8QQ5ANIQ+JdE#3-`aw%xvdW!r)bv3Am;o{H^;t(G&x10NKSpw-lrLzAJh8&l*5myW-jw!a97jJmBNwJ;yYU@Id!(cO=u+^tTe;{5OD}dPyNGYlH*UKQ;`27U&cSc~^dkI_fHXYkNE!HgQZLl+ikOdjj7O)=LPw1H2IW4>IEv59o;d@5cn$d0()2IUPo8VxYx~zAuU!2LcH#3TvEtuO{2Jw&9nOOPs6BjZ&UyG&%7Y{L{B#v5f2*{#zd_qCvWxfzeb@B*U*Nv<O{eks$>pfW;r#>JY2}U<-%R-{%8y)q2;)|(Eqr5KE_|a}h^!A)Ys1$%Ew~0>>x{h87isXVyH$`Un%CL`xc~mCQ}CVBQI9quJJp?U1;$_<(7R-a?_C-7YZp%Lg`YSUzVT@i`b}>T2j9voDSq#U$U{e))IG?D;%9Qu&P6r8LOrv;JdApCroh(=N@9G?n$@54E&7g$K8Nx7m>*A~p2*D8c;5J}2W9^B5kGaUls~$6KguV*Dt_=_l-JVqeJKBXIrzrRa_3P`r*l?OUz;Vq`Rf4-pI-?*fp#u9jd@{srbs?CeF?r+Vy3j;_xKUC`{A?WC?Da2dYn0f4&c56+u>VRQ_v5NZ>QjW3w`~X_|Cxh@V@%Jl;iUGJ&dEie>w8ROnx7}HXvX6VR9$5{||ql_~zN>Xus)Yeu;Xj&BQob9-EN=M#WX|^}XHDPCYyn?Qu5CKZ<&qW=elf*?Od?Z_u|IESLNby&>iOZlWGnt0t(Y&^PEi=hwh{S;2QupYh-_-q(ux9`!iQ*?14_M3Xb9Co5jsQ|O-*-x?c*dK}fKh#xvw_Lt^y$Fhs~27Tv^F~`u(-`l{~SDuh{ps&m$=iR()_&1~BYb~#>bLU&XEWmoJUyQ<fW4*leI@)o`YiG6_-wJf?z<XSKjQMBX?2GwjRtu3luQ^8MWzrz516q%X``r0vddNOJ_gn~kefZDZ-yfoX3w?{e!S%%0<FNzvTv!6%_1+xxk6v-^7Wh>&Fn^7K4<wIYdu6lq^K98iMlF*33q8LH_pR-k2R}yoO`jOF5ufKB`xgCh<-}%pzH{kxIfq0}lKp>cEc(;obpre2i@v#ilkAUa%h#a3)^m`z=5L=PU$ufuOHu#DOzF>dPtfn$p{ol~{%NkP+pjF$<IdL(MDKy-te5~j8jJkYP7jy*ryY#Nby|1KAFZ%|o=jMX>-Ke#uhs$CXSG>%R^WM;<1tTNf4}${{5N{8fnPlm^F<$8LDt7RT{oeg!1CB{92IBEdNeK>{iIcHC+*3)oQZk@FKxm7&z_<Gt$68wqjv4B@YgNQlluCky7Qe6e6XHtQTyR*A869fp|j<=*S6z4r8nz<@iJSF*y+}Hb=-;j8{fiyZp_$$d1WLuNB<aKci)cdI&aE;RK**4u5~#ge*2##pT9Yk>CV^NZ_dQ~6_}Ve+K=<lKYATGUl~(9kQbWy!*uvN{iOXjX6}Zc`W5Dh*5<LS*Y|dapA~!@&kb#ug?#&{n~cA!-7NI~<tmuxM&u`Qf7Xys)wOxKjI5{s_)h#5X-UwYN929;-~Jred#}lP$?H1zzn<71v=uqnhpd@*Wt|!lgMC2j-eo1;yW?%FgWB7lir?Wg?DvjkJZIjXkqv)-xSW?R-<N%K{vPocPlK;7^WHD{b_n@uJW7&v)#)qiZ}@ebJB-+eGQYxxr@Ql=dun1_t!a1VoHBW~<keK3HwF|)`9~?(KddKy7#HjAQ}G{WVH}<BY~AV3*S5tYfAkjfus&%eHsCyI*8Uj%rtesZakAEx$M-T<ela<J)H@7c^Yn*r-1uD9@ja8}T)x|hyf6oGKCbyr)~}{_q#nOBSof^&!{prWR~`GK^W|gd?tDFWs`SI*$MQXA<T0o-WsICl`gNCcb4(!K%UHcW&7H5`cjCNi<qVSZcfbPdU*_v_&ew*9iNCBB@<glUly%uW4d2>XLDtEXF&o|au0ehqalLz>oCE5%#5~oVGG1DMhUXb)gJs`bT}#eei4}3Jy)_Q%$TuWUa(0TJ(fF+NgO2=n-FQvbqx6QzPgjGG_3nK0zBj%X7+NrVLpS97-D0H7$7ga5(DKV8e;vs(UY3<9`&PMdIrsKxnd;6r%jC=VowR)MFPXBQ)E+C}YhLgjsn=wlg$3qHK6l2x><W_panx-C-(J9-lFvQlJWyZGCC0ttSjSwy+2a-R+^-&kJ68zYSIYjzYez}VSBn@{^e2x}Qmjzj|Ku^c#eemaNAqSu|L;#8AJ}bJYDc0SX?Co#BbAy+PGp%>mQlKqx|FPRC0Xe*veNbB^}Jtkv>j1)%%@Hur%)596UYhVNesm!s8Qq*<lzj(Vbo}H7&(Tacph~=xv(Ac7>ZXj6mMfFUPDbFub?iVCXg49r&1@8r;^{ZV-PihI*B}q?-s!_O8Zksko%MSQiqfKl6x~0_o0T7`;hzDF_0Qg4I_uKzrtBY>1b*Uc{F(nbsl*N`4j4D@+ahEJJRjgWXBe2GC7%Lwotc`w~*5rinmhNkPF9SD|It@Gw)ICV@G8>s!;2ZtB~tb+mh>&8&f-x8<XFlb|b$**6nCd?Mm%N?n>^-P~4r`iQJvsh1!<fh1`N#kKBS>n_8J%n_QOaLoQ1$X2(m^@>CzP5Bo*2(~gmLOtfQ>9Us||#85n!I*~k=97`QZjwO%MB(IbXppGODAcs<&<WTZpJN`@^X2*Ct;_Ud)jv3UM)Ht%zc=8PDY-&7t2Gw9Fo<@x)Pb0t2P&}O)NB)31hM{;eHI5v|c2A~`B~K=gp$;ojkK&=!!Q{d0lc5a7k<^Lgi5#0qhT>V&MdVrJg?4PPW4Rq`sSC*qS!ONEC|yTgL{^$a-as`OiWgIp$cxDzQ|FSE#*#lKkE4zv7v|77_W2x+iQ+_F&mk|Nt|BW<BddAZ#tyZ=cO@(DZ9D#A$Gg-a<afzEsJ+O+)DUVf@;lU`*Kbi9kd-zq!u5IGl-!6KKyE~CMhzq@ZA~s=$IEsUXDBYsQ0&W4T!~tOT#5WDLvclF8FEE(1%~2M48>m55@av32emla+m32>yv9)6lA*XcLvbsH;_6gyavf?psyA7wM&|!KX`WOMvIpDa$xvL9TAJM1jyLV-NNq>%NbW#wLhe8gqP|WJA~&Q~B{wAdQ(qzblWS2+l1s8}wHS*1sJ>)BvV&TQ>>$^mzDibFkz9jZ(~gjC9>sh;|I>f<{rk^Q9r@gU{JnVR^T*|)cm8JA^~d2kq+4-}TQU2en$SO~k=FhN>{^!~'

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
