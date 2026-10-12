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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/65c6ffa083c6496eb84a0aa3c48d63ad/part_000.stl', 'relative_path': '65c6ffa083c6496eb84a0aa3c48d63ad/part_000.stl', 'source_sha256': '8edd63a8a34e4aa2a715b1d3b1e5610d39b628f9fdbe988e035e7ee93976abef', 'input_faces': 363, 'input_vertices': 218, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1830359697341919, -0.4691144824028015, -0.05036970227956772], [0.3017338514328003, -0.14085471630096436, 0.41842082142829895]]}
GEOMETRY_BASE85 = 'c$}r03shBA9)}MiDrnj?Xr)%S#4sYKvW)EEt)|Q;h&aCWs^B9N6eP_TN7F=nqm+mb6vc#81jX>ty*|=Z)I{LoBfC>$_L$1COxLnzhJDU=uIC)~tTk)quJvEv$M0<S-DmH8ANww2x(C(|RrJS$O8Lpm%&WD3ifW>SDsLquPZ~QiA*Frdgtr5fJGERq3@-20w`a_N0Oc)ZT6lay%E;vKPLA;BM@5B4I>JXKB~MBoo;WNiIX*$;uMK}QC80J?88duBLhaw}o_r!I($V3ONXHDv|M&<IV<;Pcv~w*yH-j#@Yw4KfThrN;JA?B+7rEj~iE~SGr(@1Gb9*%{{i4V{8T)eFl00|B7rV^uJrRFBueHl8&UZ_4&-|`?%<X;Keyq{*rpLFqCAr$AYOiHHoo`jk`ZscW|ISNsRkHCLxqbX<T&GIe{1~}?ev}07S@S%*?pb_7Yky^-e!mlkd}hvlr$%YHTHf`PEO&OyI%Cc~T^`VK*ZiXumi*|lb6P)7`Ocbi=k?3ly!n3ry3&%bQncJT@Z&1WI7{k#wSLs8)#hB8_LV+w_y20i)l)T<viov0I-}3eNryCdMQ2-b^|M1-uHGs?Ez3O#m6rBOcBz)<Ht+2<=dQDx_2+FIVwpE3a-N>Ac;1>{7^vsR60G^=2)+M48J1j4`B__EU;cV)`>--CSJO)@xhrkDmU}jqN^{qZ5ti|L);p#BIAa?~pVxQ)=?d96J>RXZklmLrJGnwO59+nv6|#BrMZQuYn`h_srz>RZ;@RJ>LbmQkZeMrj4M&A+|9HB!I3wF{xnbX(mhR7f*G|gzv$8(CT(<v}-%cNwy<U{xb{><yzJ6$XO!hi8a{KF4-FNO&*?lQ}t{v3o^P4A5TIONu+=J%!xqE9Y`@}Kk=y`MQTvn*fkI%i;k}E6EYxCoq{IDhWysT>Tp!}A2&YY`XW@+PBzUWtD>1WuFN3`dSyT@zE2V6a@%};P<m8Jh*x*gKyp~bbcmi&iQ?Y^9CTA!5Vo{-22OaJp4TIRvm#;47<(*17j^Tl{yHF9U_xeMC5B(|C>%{OL$VCiREgqADy#!q(3@;gTtS=zU~eqQ#xj<8eu`*YuvWwKnYe0Y;NSAQC;=QnmvljY7Y#}-)f3vKkzi_0gLx+S^m*)}DX_Oo_r@BfNg(ZVgs)o;JwYHn|Qo;qLJvcfINmC$G6Wx4BWo9)tmmbTn!ng5I7HL~#-xqUp&*=1hY{TjLbesia$d1doy<o5aWJlo7GTQ4KGub1=HE7h`f_gyQlmhB&ZZreZVH-Xi%{prtb`_psRkt*}^IwF47#}ji&Tld_bQ!Tk?P^p&t{?%-gC7%+j@1G~9sODVRT&(Yt&5v!h<X!XiJTbesrJvAeYGk>uG@?e<kK=NNSNgp5!o9L_DlPw6ZN4w{=CAtuYsWJEd*i~!ndV&C-BW)(&i-bLIrs0|9@)L!vi!=VZRYl#{3TvlKd$gFulad>U)<E&M@3rSf5?^Tf7jnPQiA8ma#z@;4=j06l-@r4xoK`m?z)y&WO?4nkLvS~-Z;}O$<>EaO3dy3-=ACG%yLU|N0-E%=Jx8fBCo7}Be(bO+>=)=8^4j;$M5>_rz+X}7<rxfX}iO+|JA>B)IJBC$D;Ik*b$Ru&Xv92>-%;?O};tzulw=lGiAAYYgd6e_iXrwSJscRKF@1@US;1wy}kWBMPBDTWy}5N1@b!QDO>J8j~LHuKTp|m|9OYJ&Uwm~`_EIx^V-i-w%p!-o%56}w~xQhdCHdC=f{4Y@@zk38NdI1GViedJ!@9=MOmIZDnrYavtLh^<(~Yn3e34j-JySfcp-bCTax>po>y$?r`33UU2dJvam(_P-|aHD_kV8o>6Po2<gTbzyDk0qO7cqkH*#D5>bDWqvhf>vo$&|8R!QfF+&(|bw?Wp=sem*3{FL1IT$=CB(q9)V;-lS?T)k`PHgkJN()Sl-{rFsK^>w^>Fjbc4hP5j+=edn$>h14qp5vC}&Uw3bncKU{Jo>svtBc)|+||`nZ0SGsg8n|-;PrgBB=@}>y2spJElkzhuWPx+Ey<l%I+j}Q%Xs~M-EWIqk}C(V=gM;DPl>x_{U{w)?=|Pn;?Z8&c#PaW9?vg|S9ZTfUgv%{wyu`Vr;*#|)7f`em2AC?+`eAQ?=M!#_Jfhz_k;7+)k@jEQu4c0%J!#`+xMqZaM|*{q~=8H=SbUm&B*QNH6yp5*NohLUNdt0dClLC?Y!pCZRa(A|F-j*KewIN?74AX^Y?E)uf<q?Eq&=$NYI==D2k|HB~%$T-1Jka2*tyo{HM~fPyJUvm3HXZ;s5=qv~}$m#86toJMotIz3?vlUc43jBi;(X4~F9R;Sa#(_yf2Dw!j_ugYa(rLHr?j5B?C|2Huai!NcIgco^OmK8Cl&!{L*7INlC+z}w-Ez^Cv>@Cf)c9)Uj!JK~Sxk?<Kj5^oQm#oObL!%q0)_!G7DCm01g;ZgW=@OfOY3;rDbDka=Y2|ov4!_VP0@XvS+UJYNttMMxMGG2vO!k6$${48|hXYmTy8Lz<4z!&i|_-F71T<|pBthVl`t){Rs-V|>FgYhPK2yBRl;EgEZ4PX%70Iv@Nalrt*K3<O!E*^Vo%Trq`;Cpx}*D~P>d<WN-!c2TS*A~O2coEl@z{U73t}TO0@G`C~hs*H&T+4#X@k3mDA7<f4xt0yz$IH2v1GDi{Tw4Qk@RM9y4cFkGa%~k{jUVRPO1KL5aP2*~5^qMIcfcI{4!kkU#v9|o@O?ZOZwRyShIkNMjtAj^a2Xzm2f!tG0ItBr%I$~ndT^<7dyfgP4>Oh9`%riTxI($ThlMwS?<u$Uyzmg_rx|lC*c4xluYyhRRrpF6f``zj@B_8=No{>V2`_-h@B;ipcmn?r-$n^PuIT$g@Dx0OpTf)GF}xf<3O~V*;)mb?{1Cn$evI$O%ivzT3^!hLg1g~fd^f&<621|BjBmvA;Q{;rbC*vEpG66O2NvM(;B(=J_*{G*+=kD?-=&0ag~#!&_z}|@9D$$WNAQF2Fn$nsLl5r8_rX2*KKvtCihqRfggfw^cro0L7vm+c2rptiN+{vEa08x;Posp-fE)1{cpA*d^I4lTO88$W;e+8j_+We_oQsdd6W}~N0Ur(D#Yf|#DB*M9R(uX#2#?@LSf@ft_!j8Kx8R%MK72F234Vlc!t>xxJP%(Fi}CgNI#`02upa9u;cvrf_}h3_N_clT1MiN<!ZbXMwTY#K_oIXlgoE*c_)s_!ABwwR0`9^`z|r^!d^jA1566d5!sFo_JRYA73-LnMX*MNXg`05|p9weNGx6y#51)=th3oOD_!PJfU&ne(p@hE<yW+3oy(r-^usa@u$H7=UmbHnaguh7%p9BZulko9yC_Wxff-XD>pA1LflktggI6e`d0Egid@V6-8gJ3*92p<Ax<Fi?(A(Zd|a3($g?*pgfeefP|D&7O{2B+XtSdVU$@Sd<2-V+}~2~UPGcryM5jKkwtn>Q%o8E_IliS@{!gfD_gcoJ){2u{Qo;S1ped;;^nkP@B<2jPi$e>emm!u<B9g!hGg@V<C&*aPp4N5gJ-H|8;#5<V7=!N=n1Fd0u~?$Tifo{q1Di||F<^IA&y0+@&|z*Av=yg&DrN(mnad*kEq6c~+1a}Oz$@cA$uPiIW?;R1XC&o>{A!&9L6JEnU;z0kn_^xxfXKUD1iX8zA__J3*p>Bsyp+c#Hk{}2?@JxF|auKmJYPupBSh+iU<e*^m8Ggk'

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
