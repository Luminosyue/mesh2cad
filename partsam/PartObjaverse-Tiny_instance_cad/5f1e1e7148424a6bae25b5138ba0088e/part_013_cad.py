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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_013.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_013.stl', 'source_sha256': 'dc115fad2aff02c28d4d1db541e8fd9586af1aea5dd626cb33315fc6331b1c43', 'input_faces': 352, 'input_vertices': 259, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23380041122436523, -0.10984759032726288, -0.25219792127609253], [-0.041236989200115204, 0.033516302704811096, 0.3139341473579407]]}
GEOMETRY_BASE85 = 'c$}qL33yFcyIu+M<2TlrV>(GxqK($<H=nkqOI0dpw8b&RP>m^KDzZ~*XzTw`rA<y^$B={si6Pn|wxOgXgqU6JHbqJ(RYVQ{-D`dCK6foo@AKT}-t#=)^S<j{-}&~pzO~j~>xi&EWy;oM^a)^9`b}t&TbD6zl~_$SEpp1#aU&z6Uz;##rVpzobpEmNt9J(W4IAvkrm;_gM@2@DoD$r@8Qf{~KY~M@!J{WmnL1_ogkck>jEdxXkKrFjM_PLH*x{2Rt#(MuHtj>5t(t~9=Q#h5pNc$((A)WYEikJ0T_JG78;3c%UL{?dv~-=o&^<qKbk`?c&w5Du{%5(uzY6@1J=rMmrjLljDv{21*H|VnrlasT%R@icEnR$n=)*%I{@oJF=Oc5y&}+~8k)!iA=`483CJ}$n_rl**OuDOU&|0B4T_WPU%@QSl7Q9R3?>bAmJ2HXtzn3C(=P5k5;(hX;=Oc6@5BmALy3nJiis$M_5&yOR@glC7d6?<}{k=djUafy8%4aX)eBF}9+v$;r!#vOf7gIjV4%2g2V7#ekHwgc@4m2<Gp-&#Ql=8nX;<H)M7ljFb?Es_t&p`Y`twlYx2j?lDzNDL%1I2TV`TGxwarHp{<Fmy)vZ$IuH`|czJbpsNF-~XDc+Hz?{?89lotxfN=3Sdc^R5j#L-Q3hgz}#~netCMrHog5lg6vBEmZT5qWswx8OnNK%V<5gPoz`+)weGZdg~(L?_A|k$Mw917#EB4sC8>e>(-bB|NgyGM7}jzia7cN(p|k)rU{%lgZxK9UpR~E@aPv&2j+&}?U{(94J@T`4fCk^m!tf(fgWW)YAa|zI-zUJCvFz;N|MQcfJd1}?LOwQi$__XEClPbvqzoBZkvQ|cJL^5(~eQyOn;BEA6X~bkFM$-W#6%WwC`9|kFp-vd0G$diqHqAi2T`&)wF*fC19UE_6RIIOYt8jDErR!4edMj8|kh}t0{iFfFlBLC8+D9Gp!Tz2K)~!%oP1~&mR!|S4h_vkD+;aGlcU08F6Ah67$RM#nSv1AWm~e`|+ibw7-s$&Q8Zs{og92@$N;O-M47GR}w}3&YT2gowHP0=h}AUqn{LcvY!^v{BDK+nrBr1C&MVuc;w?dh@QJIRn);;fO;-_zL?fiEY+v5xl%W+N1)J+GdX!8udCOnK6^f+_gm$~q-(25pL9;tjm?>tr^HYEjGpT|SLm$S+?@iy52g3&gE>NXb>6*8_=h#jlXas?z&En){+V>MO*qYO(01gHIClQuQvUA4q_gmC*|a|1%ae8egTNG7*K=OTr%qdur=Cr^JAFOn@3)`cV@dFDa+T_EE2u#D#gnc*UAdj=@e-|vRfsd>rto+5qI$Bgkx$h)k*BM7zF6nxLc|Ho+a~bn-wR}&4frEn)?M=v|6;N5XYXF2bu|xpVm+`-s+&8Obf;fe%5%r^d|5ZXtdcJ4S~UF2CjKDeyfRbK*&m4>SvRBLU$YG5Uu`RmcMQgrHcZr0+qLMZtQ$S^*U7pWsXkYGa6#15?M9r)$5~>0o4=-gF%)%((6@?qc5%L}v*JFRW!?D!;&kgH;%MQYi#SFE^6`Hl=1WVNujtx<n~JXYf`4hl-9n$e@rbOmqWGP%&U!*`*qihN1#}*{kpHwbJ4FACiutn6YIRGKb*&ZF&-o0BQ{SZbOiSo3_S1W#Ze_8qSaamR*|So#Ba%fvu2-P{zKG(q9w&4yNL}abez{{JK6I_p>F)&ox<=8h7iqGr>kY7f`)n2SVqBqfiq(N$dR?qTme!o^Gqq9AG0~LI_OkTesP%$=iSA>11$Do$k)6eOji<Az4v)h`eB&zJuUxi{eaE&eJTB{O*5@g*&hC?LRNO~(2&8%%TcN*`DC()5(M8>y@3m9wd0;H<yW6jkzkM%y`H{%qY!E<o$WNj8$@E@zrZ_1M?k9$W?p^M$pxftiWjdF&=}zT6%pw=j`+Own-urwe-5=c0z4wG_2Sj|AAL8KrWq0ZP)vGk1^%?sUz4!jC^dmjLfx505uA@3Y_tqznbYpaV^7pSz_p6tOQ9f-+x9`KOE#|8k>1^^7x+k-%wBG}u>qTN;7#U;fT>iZt#Sbo}-yM1x(yx$ipX08z8oi%Q(p@*k(0SVI2T@PsAmZSD#inE3CPT+Pkj<uhp!p@~=8=55A2$0N&C3GP-HDIMKZovnPUzm>FHyMfO-G)6FN*pY;qA#EI{WANEy6GTTdL1E<e%b0`F~zY_kj<QPooy3r(eW<8~KcQi}XhH{?XdjQ`RSY`3UW=W_WIep7h+s@$}pf#K~Dj{v$UEf2}d}JLhSggwwsn3_^VTp3<uO(tWtZq3(-Dx%Awfs?J`g{o>q2x_z%^wduX5edbWl)1*AQH_mXV=V=ViP3Ye96uLIiq23=FMC8f3_x=Fg80}E+58dhhz=k@M_oQo77M&M89P0hSw=vxxx|8m1oJ#M*sJe6yY!5y57jZ5aXA@}MLie6K1sjgYy7%09L3ifkehA%Y?oiL2ybAfU?mc&)>!A+iUZGv5I9jknxmU1jxIaL*?-gFXo<lv~BW5bPeXp=}!{JchtBdHpYSeP5_l+)e-*8oRsP~Ou>0V*$-uni0-Or)kAFk0o!PdR^2k6FQe`Q@6*`4T|EhXKVTuSx4x{=Pc+y3f#)DFM*i%EBf`%~R6-J<-j!M{y5&3iw3Uzx`czp%D=uIslQw7>EZCu9h%|8lqKy?4}KJ+JGmJtphk^BTGi-Fxl__zB&0z+YMCtS#NoZQZ`N+q!eFzk0r(q4Ql|=dbKj?Gl}{wr-!lwr<8OqjP=U*ri>$-ezPWM^?Y8qO%K3=q_{pR#`W{n<jMg@)Sikx`YYceP<xecf(Ga$U9;V>3V<C+ue!cZD*3IySvs%ly&`Kah4Ka&ps*gT~U}N$2Xojgum9KAWM#KyjhRpI5Q}Yc6+AK$9|#c+S38?vhEI?srYMmMk%`OZ|mBPOLTuNd3CyoyEpHoth<MoOHlNX)0uMqtX(3-xp0EkN4WW}sKXr6+0IWh<vQr;lSLdoelGp~DW5%A<Tqj+jq6x{CBA;K1L;~nCB6~Rk;dieqr`C)V_w*7aXz^>ydEd~AI6=Ob*)AFZ)DxobPb*Bx%DChez>Pl*0sV%Bf9>D&PGg5`YT<l)HGSvjnGa?9P{!@MYrSFx*n6bNzO-SA5i?~Ss6m_@ctm-_lmEg8{d7jTGq{|o*7D=`=6ouOun2h>&|mqD9*=+gl?=GA0y_q_lA?Q?uw2{kaay#PnYL~b-YAzf|jSt^QfI7-TXCSqwKH$GK<#F#3dV*eK+$H@*iHZL0-@7?cWsLUeC7fid>-hn<sJ=-S)S2_R{J!dEc4-&lKI>*S4;$TAC*3>E1@V>s+-odA+%k3Qo$pz20oyxKf%b?+f!unNy;FZd$6mA6?7a70SB3AHDj}_*6N6EhnDzqUB0_J&x*cT>T<d*}oA9<iBfSitO(!GHJi;3{Z4eY#os&b1z@7_-FN{_+=U>x*4>iuxps|SCD1jc8q1!EoxZ>R+Eh$F8v8abTH<{zy1@*xYqxxKY_Gr)AIlOCy?HJYg)Dj#(65R8+a=CKHwnmec)SwAA@tu0Uuylq-C3c8^MR5ZwGJ__;~agz#ZU2(U%Q0zz3plGcX%`H2Ttko56W*Q;}Z|_(5P8_(AX_;M?Fy;Ol_zg0BN#4U7R_4gMoA3Y_C!@c%%r$-s2*_tCc<m<-+neH(z=!S`D>4}1gk{V>imfyv;>$RQK8KZsf<BZs}PbmW<i8vY2|jPY$o&F%4KqaN9qBfCBZ>Sy3NNx*~PIp92(G)8M~8*m@^HgFw&8>M;Vd<#$q*WqvTUX~4pZG$!v&$HtXhBgK`0>*ha;9zi$gCyPy?Lpul10%sXPL=oow5NiH0f&HxfxitL5B@gzyTGB~9Am)wTH@>GJ?I0`7Xuyz91T7izMS)Q)g9mO4xRJqXul8Z0WAtX_L|{56WAR*6Wm^>`|;iV&^e!G*@u=*0Zstt7y-_GhM}KxH`<&JN4vje(U$cC_66rS5xgJb^#?}0z`1>3*(A$)1K$GY*aw{ZOh!NFqtKqgXsvt%o`yE(S!l1dEXA@!;4W~E2f(?{cj)JQ58Ax%2g`N>cY|}>3eJ7LM?dH5(N08s-kxpQr<TnD{~B$M9&nBc;2bl+xqm!-`KN+qm4Ow(IhL3B-_hpi3(m17IRE${2LHT-Hpgn<{8I%Q|CB|$nPr_Udj%K(&an+R$Hw5?zZHCISXSFIKVU6zu9tzvu_`#na^M{Q2G0Gf!#B>dPb`}S{x7sS{{n5!SE9}NGPF7W2JL3Zw+^g4G=IyQSmppWl=!P?`=drpz{{dt7e23nH$=NG>e>*z8rr<?AMocq2yM<=qRn|{v^npB_Bil2!8@bPc{tj9UCm^)wlcuOfjz;y0(*jYmh_g=v-or7z&?dmiP0J?532)>*VT!6s{x&Be(1MrUISXFWg(We05%7ogXhi$b^-5#TFi!VJ{Q;od@i^KY!2Q6yeY5=cx7M{7=u<BIk$i{l{7o|Q1o%F7RF%fe$e<jZUo*4KAiJ){Dx&?VR6tj<QEGJ0gnaeYrZwU+Xy%dd=~l}0YfCd2r)P=1?T!_&^TX!Hs}9BoBJ(9UK|&LbNnYb_nD9WSj3-?zRxiy99MvI{0f}=e2IR}m!Pd7{u1~tXEf&=zXj*G3Y=p+_*}&2zV#WcQTv_9+s%Njz}qoer-8t>5^sz)_i;kwyaU?xfE~bVNP2a&`TMK^qqWcgb7J$C(dO2k(cE(E2+sA_p>ZCJb|ZW@7``s}a~uoK@eN6T2ighC3N5<~yas*`cnx+R+CA{cz-Qo(!S4cp2fqtm4Ez<m7~BM21vkOZ1OF5JJa_@{BzOUMF7PMtT<{aXLhvh=<$<5T7_Y!Me;|#YbAB*BK)V?E{Q@hI#!`Z@-a{?Kf$Bs24`_G6@4}z+vl!b^V1dNX;(2HBJQID~=MXR#JQw4#`3bc7ch6XM5qJUoIPe1O7_{TyM}bGckAj~Co&mpO*;C7&!+wKy2fPG$TN-l-+T0#O`vd$b@Hu$CW#=qA1-t})3cLt-6TArgPv9f)Kf!%`2>%Vvjq@kaO2MCi-vHhMzX5(4_%rxv@O<Doa9+>D;Q7e=IP$!X_I1p~DQRv_p@v1MLlMUC6#8|kkL$iZgnT@lhxPICty$)O`Y)va{n5n5PyP?3FMd<~XBYXKe%8gu`;RbTeai83&boB^ii`Ri{O!p83yko@Qv'

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
