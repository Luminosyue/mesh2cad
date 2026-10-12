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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_013.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_013.stl', 'source_sha256': '574a9fb81a21bc0a23b5202e93f13c104f81c5b2c33d344431be5321ebedb5de', 'input_faces': 298, 'input_vertices': 260, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10394550114870071, 0.2981984317302704, -0.1378096640110016], [0.09509439021348953, 0.5000038146972656, 0.08543659746646881]]}
GEOMETRY_BASE85 = 'c$}qL33yG{+TMw@M9no-LUvq{7L_1HROPr8L#9S9HALA#C|ZexkV-jJn${3Q3<)Yb<}t{irpifODm9cVQnMqas1RI5tGB&tf8Tp*pXL6~^FR0IdEV!J_j}g))>_}%d+oK>Nn~ghxB3eIc`MatTu!q$Ruls@l=@0iY{JAbBVrTVj*m}vQR<Ly{5d!yqJMbgAQvS`nd&<-HgQCPZx_|K>!{AYZB*Y;aS0O>V#W`POBfkz_&sAjNQ@PJ;`=f2vEusG_8tA(s2yHwqkgRZmw(ko6Vx^<_ZA7(;@4dX5^Nb7vc|Ypa?<vYzdiDz;oEK;o@ZR!GT+-x{+q+k8NR)4zqR!FfLF=4Cm*BoN}t~+8`rvbQ!bxB`2v-19kQ6>>v>;N`4;0Tj^)XaE#&_?lYG@0cAnyPE-Iw!#)<3?ZcpW{Zhdze*OrbW$k($osa{L=rVUhIzrS(((p-vT>6@BQ<@bb>uU-9++nH0ggRU2J;5dV#D89N(TWt2#FKcl8qBX_FwYA{ME{eatCHE`yj|24mduQ1%)hLcl^IA*g_Z}x-z5L=OYX7x|DOB!w2Kjo(U@EV@QL>c$!YSlyN57%+O6BZ4%1`x)9B1W0t~c>p>X$NaDA(&fiF|$a6^f(u?8oJcXHXuLD@PX+Z;9aeV;@q#^yD62P`Q$BTt4YB#j%w4`kb!EzQW~OU${*9IcDES{+%jZJ|=?NuN?VlDt#XHJCEB5h4Xf{7u`P&Uu#y2d~36WW%T)L*T~mXCiD2dGIl+USFchozcZTi6Wn_l`E^UkxBL7=?X-C((>Pf_DPaGLdSw)+T0_deHZF_(cen8P&O9=MKA%67<9m)gOL6+2r+hm6KgaRwiK*1S-u<|ITpu2ni8FP2E@lOA`vVFn&+3t7^XYq4y*LjEC;2%l+`fv~r#8pG^@Q4K+wk*e6lb<O$A1vd&sWsS<y3C^l>&1<ZI|z-)A(LL$9~QYj`PRU9Zvq7?L01B+&-W<eM;F+7|wZ{c47vV_ufmsQcbZ_Uf!r}qjJ9U$+vfR{hr3j?cN+Gzp{k$bG<Bw`W-x-<F~L-KCN{><L7^1F!}nVPW;?Wb*FLHz6vTZkFVkxl1%;uKaTT$I`vD9oIv-db!Zc(dX-JtA5i(LZtUL+rug<d;ftugrq}b$?YFreN_X-DTavGNK3YJ28IQl-uRGPNWdE_6t`8KEuPsU9JYQ{*OMdswT>jWvZjVPzo$6ol5&7!;_bI+I{8TjcW4ndpxIH{W`8>z>rP{tV`!D%Ze0^UGJzq+bI^52061iSw8QpJ|A%|!_&~EqR=i+eNY~md@^3_F^9A|nb%7eCRNgh96FYt4%zqOt|&+_3o3yY~es&bt2U{8Na^Q$(;o5oRpXyty@{gHe<qLTYNZ7j|I_QfZ;e8xDQ&#N}eq<B^Lvwv+p&p&%6ttQ`REBW@dZ8^`%m0o6F@7#ylsWf<P9rY`f=X-Tl2FD-Ra3|&ChzI+h`t$q3lb<_l$bEVa^z8jyzDDJC>PM9u<lFTu?r&~E29@*vp8Ziek4xeBc|j&$Kb^qy1M+P1-OBHcV;$KKh+j#07%`XQbn>9~=*hMmv#;qt@%&I}UCrZ}#(uXv>aX?O;mt+VuTR-;zn|N=C4Lsg856_)M>RQb6*1vdU-ho+pQ&9+{@6QH=ss!YO1|2B7yIoFtfTUelDAX8hBYK#jrQQ@%P*Dh>zSLVUi-l8v>=nOwN9b_+8g(x{#p)>XTM=E#j(1!-&ADs^@-t}pD`CVQ~fP3Y$N~clUzQmlGX{@jwa-5Tf+H$eQ`IB*Yd+#sl9V9k#9}&D<pohmVB*nCb!3H;|7ZF^CFjDP>=8P!?g>jf9-bA`og~SA5>mFP-nB*R~wY^JT}9heEWC5(Kx6TGx@%))npreo)ksCw!4_-88tA1=b3j$Q@?fhV4k<X(CPkE>t5Q(`5twe;#>@&{#uGQvfuwDz8~&P*hu|7<;#BfRh~b?+^Judz{NanxeX|ewPWRUiqph3hy1G1eE(NnMC&$tNORr%yx0zpq<kv5nc39-U&HvhXmf?~X;~CUzOIDPdrkYTnBpic2XXn*dOQ#0{kVhpLggx|$G?KdWzDE96hCnS`^Beu+*hi36o0x0`+bvm-WXRz<6>DBNB5n!XA{qpt2l3VkMk?ZZ<@gEe{_%ijOFYv)c8GevyA2?-FFuG_N+jv*D@eEm&&`n$mQE+^Lw+_-&at+W1Fs^{Nz35`yr$e^~-wc61{I7?`!Ml^=W=nvX+ytMYiT~uX!YkKL2<Ezn`P`^E#(X5YOiihGbDbEmtX@>R*CreQ0?+gw`*P`Ox<89_3BjUr6gUwRbX=*Pk}yb<VK@^7Tme?XA4XSK5Zr`c&N*!2LSio9+|at!lh(wPbL9LU-_cC@O^JIkl0->lRPfaDKjaEu{9ZoW<)vyhpX#<@_Fq3a9e6eGB>d$-m0}X!s${zBbO4)`xm(V3BccORJbq?eF~+-&gg*s6HhD>xj!)oac3wTyKAmG~(HdIDYUW+K;IIza<a{RpU6r_&seK{qqE>->)(Gmh=_8PR{)&`C3d{eje9`<OiAk2D^A2I5m2wlV5t5$E7Ae?+)KyJfGLq!*joMir-@|ucL~m6*~FN?vk&L-M8QDs~>mZ`@}tdvs1mj<M_TRip_JXckfjm-*`WpIgZ|v`>Wcd{_gI=e(R_WPVuo`wYc_mDsLY!iSvB8ol|@*Yc}79^WMvJYLC92<D3d~%8%N;nB#oicZ*Y;R>yg~O5^gK+W%cwx=*y;50?KYU->X9(J61=4<z4u{Ny&L@{Q6t&XQIKoa!yhB;Qu<IoHYWyMg0B_^Z=6ssn%E`}UW2oW@Hlcc*=^_28}?r@XcDAYTo#>rVMu=t;hk8T$s6w`}i1<?L%{o>5Njp?S~Y+wbn<d9~W1e6z3LsLAhz=o36Y2i_h*{gj>y-6fOuTk`Xz=US#yeChesii6pgo?nMAKfl)FlWCtM&kvTS6KOpn&nHUg{Zxu0%|DjG@t;z8X}+@5=`)AoO7oj_bk<yoBh8bx+^_{yUYb{JfibkNmFHn=|Jmfr^R{}agnW6P*CJ<U5KHeD<!lN2()-93F>EQdM|y9nQ315Sk>9^sqZ+&(l-}b?C7+|n>jd4W?<R^bt(UAhKawx6yY!m>;_}k^&Ed=IH+$)Qnup|dpw=XX@-43$m4}u5zLM6N_MKg}k}s`GZE>mWOY2zMx&`b@>tSsJd}%#w^=?V?jl4d0`11PPay^*KOY3}lpA)<;koFx~MP;t}esk<o>{Vakag+8nTHS-}OZz4*JB8K}^8U*jI)i+9zoxn$BVXR%Y2G)uyu2UW{*--r|2U^3uQ#RrroL?|`OocJ4=p8M-sjqC<nTI6+Asg<%lqY%HumLxcX%25(mq}P_BOXu+ShBnT<E>`-1$Jjo8-&q32MX8Jaaq$JeR1G#P3h(9773Qz;WbrkJ2UV%jYK!UphZg;#ROPox|9Z50U@exlR3}+)nwNr&Ar8@8xqO>$E29%jZ$>pF58l+@F2vTuV=gXJ0x8vnZ+T%jaet7jV7OIh)>CCtp67)4K1?H|N1|zUT1e^F3|Q8TO^~L(A@8IgWJRXjxvJ-jnkAq>|Ev{O8U&fAQmeo^&p1UmL)2q;pjJ{&&cK?%Z|L=Nv~mr?p*KT;P;{oa^dq3fPy<fo;<(IlgqB?C|CDWPPJMz31g~Y3tjy3%OqD9NWi>{O8WStMdL>J}1|1bz@&TS6Akb=lJqDeBE>09_ifP-t!ulm(KZBkAb_Xy!m&8NT**%+7~ZBH>H-M7;snWE2CmeKaCis@#o<G{L{#ofdAi5BY~a&*PliXi#BW$*eZ}JkY?mk;C*nUKyUDHXoEil3_TGr^i;smGr*D1k%&11F!X2OH0U(6<umXm=uCk{0-K?C2&@8U!Y{=2E`cw>d+_;8e1C($a)FiLPocL7EEQM-o(^4L+&TiQ!IPo43(OH%2L2d&r@(B11>ldMHwvr}$N|rSHrkeg_NCx@m8lPf;Lo8A&M@`05akQuuR<JylfW6!8Tft@cmi|^H~~BXIstl&K(4@Ifh_Pe=q%_d;CayFz;nU#pyxv8gL9#C5i1`sbT)Vjv?FddU}znj47~;X1z_k;z{${`KraCdy$~>TI(QuPIJ7$*F!XM4K6F0Xv>U8L?}pAZwJ#661bPYT&I6}ImkInJa2q%)P!4?_pYIdcD{v4nbcsNPz)69}DE}DWc?|zNxWp98;N##D=n}*{4&Db{2L2Yj4|*Tk@h!?2d;)wB`XJ(-0H1_DiFTjBcTb@IC*V7B@dI-41AIqb489JofG!8$2UkE>AQ$(+<<RA(oD~a{3Va1V1^o}jSidUD8SsASGtl1){3!5;z(w${&`$*H0>6V#L;ntaRp6fj4+VY#Uxuy}_)Xv`_y+V-=qmz$7q}$wHDKsl;GdyyK`SoIcc2Xz`d<PE1ilftCh!aR2>2W5BhW?Q1JFg#W#DVjj#y>DFUqrf+tByGN1*RPmxGI-i}3w&@NMXp0s#V^0v*7<0_~uU&uYOlu15+)35*5|9fHpr2s8(KK>LC_nCfT=ZVufX<y(Tgn%ZS>H*i<zuBfvcI0`xd91M<vjzYVGQN~~kcqH^l^v41Yferw-1BXC|pdF4pwL_lT!LJ4Ofc8LMYJq*B`w0vb=mZ%0O@TKA1`Bi)=mPE!9t^Dtv=w*}Fmw%p*8~CustVKuzX}e7t|!n`pe|tO)&i{*V>zZM#{Yjb0=t8~q5BH_O`r|98FU-yI^Y+e>p;H(7`mFky8@vC1CS4c!@!}?VbDI{ccFct1Hc2I1E4)kaXpo1_jN;X7<5DEm%u*IK8W>_^6dFAbbEn!1pL6p_1n098P{&mj=$OhRq&Y?%D)Z$7PtxYThKiazXxLXfbWNReu(J@zY5q3S^>L(y`a5JZFGZv*%bF>umXKZ;GDn(uyK7%;DO0=5p!S_7xoNx6?g>gf@_0sDy$8@t2`@b@CEQ)#61K)3cd?{6#6^xP3Z5Sj{!H)wwq|*Ia6C5Z8!Ll@~qv4jui+O7zH-2BLIJRjiE99D}NEFkI%Z}yQ83of&U6U3|d2M4Y4)&5r`Lom=W;ngS$h!fE$CmLw7f|u`#s2DXu@*1$vS|v_Oo&>jLiybcQy#1-K`43+Nzl4D=v@M10?fIo=dE8f995Uk68<>U<qBUWY#jJl+)B;19s#p?jizG2r*0V@z$C1Z~8K7g#H>P9RQTh`>;RUIHTo`UtES7>mz)!E+Ue40Um>U*-S$m%e9zRwKDi|KKNo(|NmV{$?{VLH@b<jSPLknAb(+uC%E*Wz1a4zX3bD>Jt'

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
